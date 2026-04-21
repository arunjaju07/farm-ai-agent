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
    time_slot = Column(String, default="anytime")  # NEW: "morning", "night", "anytime"
    interval_days = Column(Integer, nullable=True)
    location_id = Column(Integer, ForeignKey("locations.id"))
    zone_id = Column(Integer, nullable=True)
    assigned_to = Column(Integer, ForeignKey("users.id"))
    created_by = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="pending")
    recurring_interval_days = Column(Integer, nullable=True)
    last_completed_at = Column(DateTime(timezone=True), nullable=True)
    next_due_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    due_date = Column(DateTime(timezone=True), nullable=True)
    recurring = Column(String, default="none")  # 'none', 'daily', 'interval', 'monthly'
    recurring_interval = Column(Integer, nullable=True)  # for interval type (days)
    last_generated = Column(Date, nullable=True)
    next_generation_date = Column(Date, nullable=True)


class TaskCompletion(Base):
    __tablename__ = "task_completions"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    completed_by = Column(Integer, ForeignKey("users.id"))
    completion_notes = Column(Text, nullable=True)
    audio_url = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    video_url = Column(String, nullable=True)  # ← ADD THIS LINE
    completed_at = Column(DateTime(timezone=True), server_default=func.now())