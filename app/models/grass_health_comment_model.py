from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, ARRAY
from sqlalchemy.sql import func
from app.database.db import Base

class GrassHealthComment(Base):
    __tablename__ = "grass_health_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("grass_health_issues.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    user_role = Column(String(20), nullable=False)
    comment_type = Column(String(20), default="comment")
    comment_text = Column(Text, nullable=True)
    photo_urls = Column(ARRAY(String), default=[])
    audio_url = Column(String, nullable=True)
    video_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())