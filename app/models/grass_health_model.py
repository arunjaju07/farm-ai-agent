from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, ARRAY, JSON
from sqlalchemy.sql import func
from app.database.db import Base

class GrassHealthIssue(Base):
    __tablename__ = "grass_health_issues"
    
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id", ondelete="SET NULL"))
    zone_id = Column(Integer, ForeignKey("zones.id", ondelete="SET NULL"))
    detected_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    photo_urls = Column(ARRAY(String), nullable=False, default=[])
    
    # AI Analysis fields
    ai_disease = Column(String(50))
    ai_confidence = Column(Float)
    ai_growth_stage = Column(String(50))
    ai_plant_height = Column(String(50))
    ai_harvest_ready = Column(Boolean)
    ai_pest_damage = Column(Boolean)
    ai_pest_type = Column(String(50))
    ai_health_score = Column(Integer)
    ai_recommendation = Column(Text)
    ai_full_response = Column(JSON)  # Changed from JSONB to JSON
    ai_disease_details = Column(Text, nullable=True)
    ai_harvest_ready_text = Column(String(100), nullable=True)
    ai_environmental_stress = Column(Text, nullable=True)
    ai_worker_notes_guidance = Column(Text, nullable=True)

    # Worker fields
    worker_notes = Column(Text)
    media_audio_url = Column(String)
    media_video_url = Column(String)
    
    # Status tracking
    status = Column(String(20), default="active")
    resolved_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    resolved_at = Column(DateTime(timezone=True))
    resolution_notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())