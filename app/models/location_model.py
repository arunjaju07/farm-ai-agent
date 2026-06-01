from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.database.db import Base

class Location(Base):
    __tablename__ = "locations"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    area_acres = Column(Float, default=0)
    region = Column(String, nullable=False)
    layout_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())