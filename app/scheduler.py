import threading
import time
from datetime import datetime, date, timedelta
from app.database.db import SessionLocal
from app.models.task_model import Task
from app.models.user_model import User

def generate_recurring_tasks():
    """Check for recurring tasks and generate new instances"""
    print(f"[Scheduler] Running at {datetime.now()}")
    db = SessionLocal()
    
    try:
        # Get all active recurring tasks
        recurring_tasks = db.query(Task).filter(
            Task.recurring != "none",
            Task.status != "completed"
        ).all()
        
        today = date.today()
        generated_count = 0
        
        for template in recurring_tasks:
            should_generate = False
            next_date = None
            
            if template.recurring == "daily":
                # Generate every day
                should_generate = True
                next_date = today + timedelta(days=1)
                
            elif template.recurring == "interval" and template.recurring_interval:
                # Generate every X days
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
                # Generate same day each month
                if template.last_generated:
                    last_gen = template.last_generated
                    if today.day == template.created_at.day:
                        months_diff = (today.year - last_gen.year) * 12 + (today.month - last_gen.month)
                        if months_diff >= 1:
                            should_generate = True
                            # Set next generation date to next month same day
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
                # Create a new task instance
                new_task = Task(
                    title=template.title,
                    description=template.description,
                    task_type=template.task_type,
                    time_slot=template.time_slot,
                    location_id=template.location_id,
                    zone_id=template.zone_id,
                    assigned_to=template.assigned_to,
                    created_by=template.created_by,
                    status="pending",
                    recurring="none",  # Instance is not recurring
                    due_date=datetime.combine(today, datetime.min.time())
                )
                db.add(new_task)
                
                # Update template's last_generated
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
        time.sleep(3600)  # Run every hour

def start_scheduler():
    """Start the scheduler in a background thread"""
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    print("[Scheduler] Started - will check for recurring tasks every hour")