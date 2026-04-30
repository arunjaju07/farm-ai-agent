import threading
import time
from datetime import datetime, date, timedelta, timezone
from app.database.db import SessionLocal
from app.models.task_model import Task
from app.models.user_model import User
from sqlalchemy import func

def get_default_worker_id(db):
    """Get the first available worker ID or return None"""
    worker = db.query(User).filter(User.role == "worker").first()
    return worker.id if worker else None

def generate_recurring_tasks():
    """Check for recurring tasks and generate new instances"""
    print(f"[Scheduler] Running at {datetime.now()}")
    
    # Update days pending directly
    try:
        db = SessionLocal()
        active_tasks = db.query(Task).filter(Task.status != "completed").all()
        
        for task in active_tasks:
            # Calculate days based on last activity date
            if task.last_activity_date:
                ref_date = task.last_activity_date
                if ref_date.tzinfo is None:
                    ref_date = ref_date.replace(tzinfo=timezone.utc)
                today = datetime.now(timezone.utc)
                days = (today - ref_date).days
                task.days_pending = max(0, days)
        
        db.commit()
        db.close()
        print("[Scheduler] Days pending updated successfully")
    except Exception as e:
        print(f"[Scheduler] Could not update days pending: {e}")
    
    db = SessionLocal()
    
    try:
        # Get all active recurring task templates
        recurring_tasks = db.query(Task).filter(
            Task.recurring != "none",
            Task.status != "completed",
            Task.task_category != "water_release"
        ).all()
        
        today = date.today()
        generated_count = 0
        
        for template in recurring_tasks:
            should_generate = False
            next_date = None
            
            existing_incomplete_task = db.query(Task).filter(
                Task.title == template.title,
                Task.location_id == template.location_id,
                Task.zone_id == template.zone_id,
                Task.status != "completed"
            ).first()
            
            if existing_incomplete_task:
                print(f"[Scheduler] Task '{template.title}' still in progress. Skipping...")
                continue
            
            if template.recurring == "daily":
                should_generate = True
                next_date = today + timedelta(days=1)
                
            elif template.recurring == "interval" and template.recurring_interval:
                if template.last_generated:
                    last_gen = template.last_generated
                    days_since = (today - last_gen).days
                    if days_since >= template.recurring_interval:
                        should_generate = True
                        next_date = today + timedelta(days=template.recurring_interval)
                else:
                    should_generate = True
                    next_date = today + timedelta(days=template.recurring_interval)
                    
            elif template.recurring == "monthly":
                if template.last_generated:
                    last_gen = template.last_generated
                    if today.day == template.created_at.day:
                        months_diff = (today.year - last_gen.year) * 12 + (today.month - last_gen.month)
                        if months_diff >= 1:
                            should_generate = True
                            if today.month == 12:
                                next_date = date(today.year + 1, 1, template.created_at.day)
                            else:
                                next_date = date(today.year, today.month + 1, template.created_at.day)
                else:
                    if today.day == template.created_at.day:
                        should_generate = True
                        if today.month == 12:
                            next_date = date(today.year + 1, 1, template.created_at.day)
                        else:
                            next_date = date(today.year, today.month + 1, template.created_at.day)
            
            if should_generate:
                existing_task = db.query(Task).filter(
                    Task.title == template.title,
                    Task.location_id == template.location_id,
                    Task.zone_id == template.zone_id,
                    func.date(Task.created_at) == today
                ).first()
                
                if existing_task:
                    print(f"[Scheduler] Task already exists for today: {template.title}")
                    continue
                
                assigned_worker = template.assigned_to
                if template.recurring == "daily" and not assigned_worker:
                    assigned_worker = get_default_worker_id(db)
                
                task_category = getattr(template, 'task_category', 'general')
                is_zone_based = getattr(template, 'is_zone_based', False)
                current_cycle = getattr(template, 'current_cycle', 1)
    
                new_task = Task(
                    title=template.title,
                    description=template.description,
                    task_type=template.task_type,
                    time_slot=template.time_slot,
                    location_id=template.location_id,
                    zone_id=template.zone_id,
                    assigned_to=assigned_worker,
                    created_by=template.created_by,
                    status="pending",
                    recurring="none",
                    due_date=datetime.combine(today, datetime.min.time()),
                    progress_percentage=0,
                    current_cycle=current_cycle,
                    cycle_start_date=datetime.now(),
                    cycle_completion_date=None,
                    last_water_release_date=None,
                    total_cycles_completed=0,
                    task_category=task_category,
                    is_zone_based=is_zone_based
                )
                db.add(new_task)
                
                template.last_generated = today
                template.next_generation_date = next_date
                
                generated_count += 1
                print(f"[Scheduler] Generated task: {template.title} for {today}")
        
        db.commit()
        if generated_count > 0:
            print(f"[Scheduler] Generated {generated_count} new tasks")
            
    except Exception as e:
        print(f"[Scheduler] Error: {e}")
        db.rollback()
    finally:
        db.close()

def run_scheduler():
    """Run the scheduler every hour"""
    while True:
        generate_recurring_tasks()
        time.sleep(3600)

def start_scheduler():
    """Start the scheduler in a background thread"""
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    print("[Scheduler] Started - will check for recurring tasks every hour")