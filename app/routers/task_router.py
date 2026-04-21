from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.database.db import SessionLocal
from app.models.task_model import Task, TaskCompletion
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