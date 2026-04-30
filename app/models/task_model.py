from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey, Text
from sqlalchemy.sql import func
from app.database.db import Base
from sqlalchemy import Date

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    task_type = Column(String, nullable=False)  # "daily", "interval", "manual"
    time_slot = Column(String, default="anytime")
    interval_days = Column(Integer, nullable=True)
    location_id = Column(Integer, ForeignKey("locations.id"))
    zone_id = Column(Integer, nullable=True)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="pending")
    recurring_interval_days = Column(Integer, nullable=True)
    last_completed_at = Column(DateTime(timezone=True), nullable=True)
    next_due_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    due_date = Column(DateTime(timezone=True), nullable=True)
    recurring = Column(String, default="none")
    recurring_interval = Column(Integer, nullable=True)
    last_generated = Column(Date, nullable=True)
    next_generation_date = Column(Date, nullable=True)
    days_pending = Column(Integer, default=0)
    last_activity_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # ========== NEW COLUMNS FOR PROGRESS TRACKING ==========
    progress_percentage = Column(Integer, default=0)  # 0, 25, 50, 75, 100
    current_cycle = Column(Integer, default=1)
    cycle_start_date = Column(DateTime(timezone=True), server_default=func.now())
    cycle_completion_date = Column(DateTime(timezone=True), nullable=True)
    last_water_release_date = Column(DateTime(timezone=True), nullable=True)
    total_cycles_completed = Column(Integer, default=0)
    task_category = Column(String, default="general")  # water_release, fertilizer, grass_cutting, general
    is_zone_based = Column(Boolean, default=False)


class TaskCompletion(Base):
    __tablename__ = "task_completions"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"))
    completed_by = Column(Integer, ForeignKey("users.id"))
    completion_notes = Column(Text, nullable=True)
    audio_url = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    video_url = Column(String, nullable=True)
    completed_at = Column(DateTime(timezone=True), server_default=func.now())


# ========== NEW MODELS FOR PROGRESS TRACKING ==========

class TaskProgressHistory(Base):
    __tablename__ = "task_progress_history"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"))
    cycle_number = Column(Integer)
    old_progress = Column(Integer)
    new_progress = Column(Integer)
    comment = Column(Text, nullable=True)
    water_released = Column(Boolean, default=False)
    photo_url = Column(String, nullable=True)
    audio_url = Column(String, nullable=True)
    video_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TaskCyclesHistory(Base):
    __tablename__ = "task_cycles_history"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"))
    cycle_number = Column(Integer)
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    days_taken = Column(Integer)
    final_progress = Column(Integer, default=100)
    created_at = Column(DateTime(timezone=True), server_default=func.now())