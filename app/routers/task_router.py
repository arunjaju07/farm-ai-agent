from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date, timezone

from app.database.db import SessionLocal
from app.models.task_model import Task, TaskCompletion, TaskProgressHistory, TaskCyclesHistory
from app.models.user_model import User
from app.models.user_model import Location

router = APIRouter(prefix="/tasks", tags=["Tasks"])

# Request/Response models
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    task_type: str
    time_slot: str = "anytime"
    interval_days: Optional[int] = None
    location_id: int
    zone_id: Optional[int] = None
    created_by: int
    recurring: Optional[str] = "none"
    recurring_interval: Optional[int] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    task_type: str
    location_id: int
    assigned_to: int
    status: str
    due_date: Optional[datetime]
    created_at: datetime

class TaskComplete(BaseModel):
    task_id: int
    completed_by: int
    notes: Optional[str] = None
    image_url: Optional[str] = None
    audio_url: Optional[str] = None
    video_url: Optional[str] = None

# Create a new task
@router.post("/create")
def create_task(task: TaskCreate):
    db = SessionLocal()
    
    try:
        new_task = Task(
            title=task.title,
            description=task.description,
            task_type=task.task_type,
            time_slot=task.time_slot,
            interval_days=task.interval_days,
            location_id=task.location_id,
            zone_id=task.zone_id,
            created_by=task.created_by,
            status="pending",
            recurring=task.recurring,
            recurring_interval=task.recurring_interval
        )
        
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        db.close()
        
        return {"message": "Task created successfully", "task_id": new_task.id}
    except Exception as e:
        db.close()
        raise HTTPException(status_code=500, detail=str(e))

# Get tasks for a specific user
@router.get("/user/{user_id}")
def get_user_tasks(user_id: int):
    db = SessionLocal()
    tasks = db.query(Task).filter(Task.assigned_to == user_id).all()
    db.close()
    return tasks

# Get all tasks
@router.get("/all")
def get_all_tasks():
    db = SessionLocal()
    tasks = db.query(Task).all()
    for task in tasks:
        task.days_pending = calculate_days_pending(task)
    db.close()
    return tasks

# Get tasks by region
@router.get("/region/{region}")
def get_tasks_by_region(region: str):
    db = SessionLocal()
    tasks = db.query(Task).join(Location).filter(Location.region == region).all()
    db.close()
    return [
        {
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "task_type": t.task_type,
            "time_slot": t.time_slot,
            "location_id": t.location_id,
            "zone_id": t.zone_id,
            "status": t.status,
            "due_date": t.due_date,
            "created_at": t.created_at
        }
        for t in tasks
    ]

# Complete a task
@router.post("/complete")
def complete_task(completion: TaskComplete):
    db = SessionLocal()
    
    task = db.query(Task).filter(Task.id == completion.task_id).first()
    if not task:
        db.close()
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.status = "completed"
    
    task_completion = TaskCompletion(
        task_id=completion.task_id,
        completed_by=completion.completed_by,
        completion_notes=completion.notes,
        image_url=completion.image_url,
        audio_url=completion.audio_url
    )
    
    db.add(task_completion)
    db.commit()
    db.close()
    
    return {"message": "Task completed successfully"}

# Get tasks by location
@router.get("/location/{location_id}")
def get_tasks_by_location(location_id: int):
    db = SessionLocal()
    tasks = db.query(Task).filter(Task.location_id == location_id).all()
    db.close()
    return tasks

@router.delete("/delete/{task_id}")
def delete_task(task_id: int):
    db = SessionLocal()
    try:
        # First check if task exists
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            db.close()
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Delete associated task completions first (foreign key constraint)
        db.query(TaskCompletion).filter(TaskCompletion.task_id == task_id).delete()
        
        # Then delete the task
        db.delete(task)
        db.commit()
        
        db.close()
        return {"message": "Task deleted successfully"}
    except Exception as e:
        db.rollback()
        db.close()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/assign/{task_id}")
def assign_task(task_id: int, request: dict):
    db = SessionLocal()
    
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        db.close()
        raise HTTPException(status_code=404, detail="Task not found")
    
    assigned_to = request.get("assigned_to")
    if assigned_to is None:
        db.close()
        raise HTTPException(status_code=400, detail="assigned_to is required")
    
    task.assigned_to = assigned_to
    db.commit()
    db.close()
    
    return {"message": "Task assigned successfully", "task_id": task_id, "assigned_to": assigned_to}

@router.get("/completion/{completion_id}")
def get_completion(completion_id: int):
    db = SessionLocal()
    completion = db.query(TaskCompletion).filter(TaskCompletion.id == completion_id).first()
    db.close()
    
    if not completion:
        raise HTTPException(status_code=404, detail="Completion not found")
    
    return {
        "id": completion.id,
        "task_id": completion.task_id,
        "completed_by": completion.completed_by,
        "completion_notes": completion.completion_notes,
        "image_url": completion.image_url,
        "audio_url": completion.audio_url,
        "completed_at": completion.completed_at
    }

@router.get("/completions/{task_id}")
def get_task_completions(task_id: int):
    db = SessionLocal()
    try:
        completions = db.query(TaskCompletion).filter(TaskCompletion.task_id == task_id).order_by(TaskCompletion.completed_at.desc()).all()
        db.close()
        
        return [
            {
                "id": c.id,
                "task_id": c.task_id,
                "completed_by": c.completed_by,
                "completion_notes": c.completion_notes,
                "image_url": c.image_url,
                "audio_url": c.audio_url,
                "video_url": getattr(c, 'video_url', None),
                "completed_at": c.completed_at.isoformat() if c.completed_at else None
            }
            for c in completions
        ]
    except Exception as e:
        db.close()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/update/{task_id}")
def update_task(task_id: int, task_update: dict):
    db = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        db.close()
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update only allowed fields
    if 'title' in task_update:
        task.title = task_update['title']
    if 'task_type' in task_update:
        task.task_type = task_update['task_type']
    if 'time_slot' in task_update:
        task.time_slot = task_update['time_slot']
    if 'location_id' in task_update:
        task.location_id = task_update['location_id']
    if 'zone_id' in task_update:
        task.zone_id = task_update['zone_id']
    
    db.commit()
    db.close()
    
    return {"message": "Task updated successfully"}

# ============ NEW PROGRESS TRACKING ENDPOINTS ============

class ProgressUpdate(BaseModel):
    new_progress: int  # 0, 25, 50, 75, 100
    comment: Optional[str] = None
    water_released: bool = False
    photo_url: Optional[str] = None
    audio_url: Optional[str] = None
    video_url: Optional[str] = None

@router.put("/{task_id}/progress")
def update_task_progress(task_id: int, update: dict):
    """Update task progress with percentage tracking"""
    db = SessionLocal()
    
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            db.close()
            raise HTTPException(status_code=404, detail="Task not found")
        
        new_progress = update.get("new_progress")
        comment = update.get("comment", "")
        water_released = update.get("water_released", False)
        photo_url = update.get("photo_url")
        audio_url = update.get("audio_url")
        
        # Validate progress value
        if new_progress not in [0, 25, 50, 75, 100]:
            db.close()
            raise HTTPException(status_code=400, detail="Progress must be 0, 25, 50, 75, or 100")
        
        # Don't allow going backwards
        if new_progress < task.progress_percentage:
            db.close()
            raise HTTPException(status_code=400, detail="Cannot decrease progress")
        
        old_progress = task.progress_percentage
        
        # Get current cycle values (with defaults if None)
        current_cycle = task.current_cycle if task.current_cycle is not None else 1
        cycle_start = task.cycle_start_date if task.cycle_start_date is not None else datetime.now()
        
        # Record progress history
        history = TaskProgressHistory(
            task_id=task_id,
            cycle_number=current_cycle,
            old_progress=old_progress,
            new_progress=new_progress,
            comment=comment,
            water_released=water_released,
            photo_url=photo_url,
            audio_url=audio_url
        )
        db.add(history)
        
        # Update task progress
        task.progress_percentage = new_progress
        
        # Update water release date if water released
        if water_released:
            task.last_water_release_date = datetime.now()
        
        # Check if task reached 100%
        auto_reset_info = None
        if new_progress == 100 and old_progress < 100:
            # Record cycle completion
            cycle_history = TaskCyclesHistory(
                task_id=task_id,
                cycle_number=current_cycle,
                start_date=cycle_start,
                end_date=datetime.now(),
                days_taken=(datetime.now() - cycle_start).days,
                final_progress=100
            )
            db.add(cycle_history)
            
            # Auto-reset for next cycle
            task.total_cycles_completed = (task.total_cycles_completed or 0) + 1
            task.current_cycle = current_cycle + 1
            task.progress_percentage = 0
            task.cycle_start_date = datetime.now()
            task.cycle_completion_date = None
            
        # Check if task reached 100%
        auto_reset_info = None
        if new_progress == 100 and old_progress < 100:
            # Record cycle completion
            cycle_history = TaskCyclesHistory(
                task_id=task_id,
                cycle_number=current_cycle,
                start_date=cycle_start,
                end_date=datetime.now(),
                days_taken=(datetime.now() - cycle_start).days,
                final_progress=100
            )
            db.add(cycle_history)
            
            # Auto-reset for next cycle
            task.total_cycles_completed = (task.total_cycles_completed or 0) + 1
            task.current_cycle = current_cycle + 1
            task.progress_percentage = 0
            task.cycle_start_date = datetime.now()
            task.cycle_completion_date = None
            
            auto_reset_info = {
                "new_cycle": task.current_cycle,
                "message": f"🎉 Cycle {current_cycle} completed! Starting Cycle {task.current_cycle}"
            }
        
        # Update last activity date (MOVE THIS OUTSIDE THE IF BLOCK)
        task.last_activity_date = datetime.now(timezone.utc)
        
        db.commit()
        
        db.commit()
        
        # Store values before closing session (to avoid detached instance error)
        response_data = {
            "success": True,
            "task_id": task_id,
            "old_progress": old_progress,
            "new_progress": new_progress,
            "current_cycle": task.current_cycle if task.current_cycle is not None else 1,
            "days_in_cycle": (datetime.now() - (task.cycle_start_date or datetime.now())).days,
            "last_water_release": task.last_water_release_date.isoformat() if task.last_water_release_date else None,
            "auto_reset": auto_reset_info
        }
        
        db.close()
        return response_data
        
    except Exception as e:
        db.rollback()
        db.close()
        print(f"Error in progress update: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{task_id}/progress-history")
def get_task_progress_history(task_id: int):
    """Get full progress history for a task"""
    db = SessionLocal()
    
    history = db.query(TaskProgressHistory).filter(
        TaskProgressHistory.task_id == task_id
    ).order_by(TaskProgressHistory.created_at.desc()).all()
    
    db.close()
    
    return [
        {
            "id": h.id,
            "cycle": h.cycle_number,
            "old_progress": h.old_progress,
            "new_progress": h.new_progress,
            "comment": h.comment,
            "water_released": h.water_released,
            "media": {
                "photo": h.photo_url,
                "audio": h.audio_url,
                "video": h.video_url
            },
            "created_at": h.created_at.isoformat()
        }
        for h in history
    ]

@router.get("/{task_id}/cycles-history")
def get_task_cycles_history(task_id: int):
    """Get all completed cycles for a task"""
    db = SessionLocal()
    
    cycles = db.query(TaskCyclesHistory).filter(
        TaskCyclesHistory.task_id == task_id
    ).order_by(TaskCyclesHistory.cycle_number.desc()).all()
    
    db.close()
    
    return [
        {
            "cycle": c.cycle_number,
            "start_date": c.start_date.isoformat(),
            "end_date": c.end_date.isoformat(),
            "days_taken": c.days_taken,
            "final_progress": c.final_progress
        }
        for c in cycles
    ]

@router.post("/batch-progress")
def batch_update_progress(updates: List[dict]):
    """Update multiple tasks at once (for multi-zone same day)"""
    db = SessionLocal()
    results = []
    
    try:
        for update in updates:
            task_id = update.get("task_id")
            new_progress = update.get("new_progress")
            comment = update.get("comment")
            water_released = update.get("water_released", False)
            
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                results.append({"task_id": task_id, "success": False, "error": "Task not found"})
                continue
            
            if new_progress not in [0, 25, 50, 75, 100]:
                results.append({"task_id": task_id, "success": False, "error": "Invalid progress"})
                continue
            
            if new_progress < task.progress_percentage:
                results.append({"task_id": task_id, "success": False, "error": "Cannot decrease progress"})
                continue
            
            # Record history
            history = TaskProgressHistory(
                task_id=task_id,
                cycle_number=task.current_cycle,
                old_progress=task.progress_percentage,
                new_progress=new_progress,
                comment=comment,
                water_released=water_released
            )
            db.add(history)
            
            task.progress_percentage = new_progress
            if water_released:
                task.last_water_release_date = datetime.now()
            
            results.append({"task_id": task_id, "success": True, "old_progress": task.progress_percentage, "new_progress": new_progress})
        
        db.commit()
        db.close()
        
        return {"success": True, "updates": results}
        
    except Exception as e:
        db.rollback()
        db.close()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/water-release-report/{location_id}")
def get_water_release_report(location_id: int, start_date: str = None, end_date: str = None):
    """Generate water release report for a location"""
    db = SessionLocal()
    
    query = db.query(Task).filter(
        Task.location_id == location_id,
        Task.task_category == "water_release"
    )
    
    if start_date:
        query = query.filter(Task.cycle_start_date >= start_date)
    if end_date:
        query = query.filter(Task.cycle_start_date <= end_date)
    
    tasks = query.all()
    
    report = {
        "location_id": location_id,
        "report_date": datetime.now().isoformat(),
        "tasks": []
    }
    
    for task in tasks:
        # Get cycles history
        cycles = db.query(TaskCyclesHistory).filter(
            TaskCyclesHistory.task_id == task.id
        ).order_by(TaskCyclesHistory.cycle_number.desc()).all()
        
        # Calculate days since last water release
        days_since_release = None
        if task.last_water_release_date:
            days_since_release = (datetime.now() - task.last_water_release_date).days
        
        report["tasks"].append({
            "id": task.id,
            "title": task.title,
            "current_progress": task.progress_percentage,
            "current_cycle": task.current_cycle,
            "days_in_current_cycle": (datetime.now() - task.cycle_start_date).days,
            "days_since_last_water_release": days_since_release,
            "total_cycles_completed": task.total_cycles_completed,
            "cycle_history": [
                {
                    "cycle": c.cycle_number,
                    "days_taken": c.days_taken,
                    "completed_at": c.end_date.isoformat()
                }
                for c in cycles
            ]
        })
    
    db.close()
    return report

def calculate_days_pending(task):
    """Calculate days pending based on task type and last activity"""
    from datetime import datetime, timezone
    
    # If task is completed, no pending days
    if task.status == "completed":
        return 0
    
    # Get reference date for calculation
    if task.last_activity_date:
        reference_date = task.last_activity_date
    elif task.created_at:
        reference_date = task.created_at
    else:
        return 0
    
    # Make both dates timezone-aware for comparison
    today = datetime.now(timezone.utc)
    
    # If reference_date is naive, make it aware
    if reference_date.tzinfo is None:
        from datetime import timedelta
        reference_date = reference_date.replace(tzinfo=timezone.UTC)
    
    # Calculate days difference
    days = (today - reference_date).days
    
    # For water release tasks, show days since last water release
    if hasattr(task, 'task_category') and task.task_category == 'water_release':
        if task.last_water_release_date:
            last_water = task.last_water_release_date
            if last_water.tzinfo is None:
                last_water = last_water.replace(tzinfo=timezone.UTC)
            days = (today - last_water).days
    
    return max(0, days)


@router.get("/update-days-pending")
def update_all_days_pending():
    """Update days_pending for all active tasks"""
    db = SessionLocal()
    
    try:
        # Get all active (not completed) tasks
        active_tasks = db.query(Task).filter(Task.status != "completed").all()
        
        updated_count = 0
        for task in active_tasks:
            days = calculate_days_pending(task)
            if days != task.days_pending:
                task.days_pending = days
                updated_count += 1
        
        db.commit()
        db.close()
        
        return {"success": True, "updated": updated_count, "message": f"Updated {updated_count} tasks"}
        
    except Exception as e:
        db.rollback()
        db.close()
        return {"success": False, "error": str(e)}