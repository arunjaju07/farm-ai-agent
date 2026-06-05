from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.database.db import Base

class Equipment(Base):
    __tablename__ = "equipment"
    
    id = Column(Integer, primary_key=True, index=True)
    equipment_name = Column(String(100), nullable=False)
    equipment_type = Column(String(50), nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id", ondelete="SET NULL"))
    zone_id = Column(Integer, ForeignKey("zones.id", ondelete="SET NULL"))
    serial_number = Column(String(100), unique=True, nullable=True)
    purchase_date = Column(Date, nullable=True)
    purchase_cost = Column(Float, nullable=True)
    status = Column(String(20), default="active")
    running_hours = Column(Integer, default=0)
    last_service_date = Column(Date, nullable=True)
    next_service_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

class EquipmentMaintenance(Base):
    __tablename__ = "equipment_maintenance"
    
    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id", ondelete="CASCADE"))
    maintenance_date = Column(Date, server_default=func.current_date())
    maintenance_type = Column(String(50), nullable=False)
    cost = Column(Float, nullable=True)
    performed_by = Column(String(100), nullable=True)
    running_hours_after = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())