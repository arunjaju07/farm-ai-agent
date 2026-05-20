from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database.db import Base

class Zone(Base):
    __tablename__ = "zones"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    area_acres = Column(Float, default=0)
    location_id = Column(Integer, ForeignKey("locations.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())