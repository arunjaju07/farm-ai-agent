from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.database.db import Base

class Issue(Base):
    __tablename__ = "issues"
    
    id = Column(Integer, primary_key=True, index=True)
    issue_type = Column(String, nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"))
    description = Column(Text, nullable=True)
    reported_by = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="pending")
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    photo_url = Column(String, nullable=True)
    audio_url = Column(String, nullable=True)
    video_url = Column(String, nullable=True)