from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

from app.database.db import SessionLocal
from app.models.equipment_model import Equipment, EquipmentMaintenance

router = APIRouter(prefix="/equipment", tags=["Equipment"])

# ============ PYDANTIC MODELS ============

class EquipmentCreate(BaseModel):
    equipment_name: str
    equipment_type: str
    location_id: int
    zone_id: Optional[int] = None
    serial_number: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_cost: Optional[float] = None
    status: str = "active"
    running_hours: int = 0
    last_service_date: Optional[date] = None
    next_service_date: Optional[date] = None
    notes: Optional[str] = None

class EquipmentUpdate(BaseModel):
    equipment_name: Optional[str] = None
    equipment_type: Optional[str] = None
    location_id: Optional[int] = None
    zone_id: Optional[int] = None
    serial_number: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_cost: Optional[float] = None
    status: Optional[str] = None
    running_hours: Optional[int] = None
    last_service_date: Optional[date] = None
    next_service_date: Optional[date] = None
    notes: Optional[str] = None

class MaintenanceCreate(BaseModel):
    equipment_id: int
    maintenance_date: date
    maintenance_type: str
    cost: Optional[float] = None
    performed_by: Optional[str] = None
    running_hours_after: Optional[int] = None
    notes: Optional[str] = None

# ============ DATABASE DEPENDENCY ============

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============ EQUIPMENT CRUD ENDPOINTS ============

@router.post("/add")
def add_equipment(equipment: EquipmentCreate, db: Session = Depends(get_db)):
    try:
        new_equipment = Equipment(
            equipment_name=equipment.equipment_name,
            equipment_type=equipment.equipment_type,
            location_id=equipment.location_id,
            zone_id=equipment.zone_id,
            serial_number=equipment.serial_number,
            purchase_date=equipment.purchase_date,
            purchase_cost=equipment.purchase_cost,
            status=equipment.status,
            running_hours=equipment.running_hours,
            last_service_date=equipment.last_service_date,
            next_service_date=equipment.next_service_date,
            notes=equipment.notes
        )
        db.add(new_equipment)
        db.commit()
        db.refresh(new_equipment)
        return {"success": True, "message": "Equipment added successfully", "equipment_id": new_equipment.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/all")
def get_all_equipment(db: Session = Depends(get_db)):
    equipment_list = db.query(Equipment).order_by(Equipment.equipment_name).all()
    return equipment_list

@router.get("/{equipment_id}")
def get_equipment(equipment_id: int, db: Session = Depends(get_db)):
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return equipment

@router.put("/update/{equipment_id}")
def update_equipment(equipment_id: int, equipment_update: EquipmentUpdate, db: Session = Depends(get_db)):
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    for key, value in equipment_update.dict(exclude_unset=True).items():
        setattr(equipment, key, value)
    
    equipment.updated_at = datetime.now()
    db.commit()
    return {"success": True, "message": "Equipment updated successfully"}

@router.delete("/delete/{equipment_id}")
def delete_equipment(equipment_id: int, db: Session = Depends(get_db)):
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    db.delete(equipment)
    db.commit()
    return {"success": True, "message": "Equipment deleted successfully"}

# ============ MAINTENANCE ENDPOINTS ============

@router.post("/maintenance/add")
def add_maintenance(maintenance: MaintenanceCreate, db: Session = Depends(get_db)):
    try:
        new_maintenance = EquipmentMaintenance(
            equipment_id=maintenance.equipment_id,
            maintenance_date=maintenance.maintenance_date,
            maintenance_type=maintenance.maintenance_type,
            cost=maintenance.cost,
            performed_by=maintenance.performed_by,
            running_hours_after=maintenance.running_hours_after,
            notes=maintenance.notes
        )
        db.add(new_maintenance)
        
        # Update equipment last_service_date and running_hours
        equipment = db.query(Equipment).filter(Equipment.id == maintenance.equipment_id).first()
        if equipment:
            equipment.last_service_date = maintenance.maintenance_date
            if maintenance.running_hours_after:
                equipment.running_hours = maintenance.running_hours_after
        
        db.commit()
        return {"success": True, "message": "Maintenance record added", "maintenance_id": new_maintenance.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/maintenance/{equipment_id}")
def get_maintenance_history(equipment_id: int, db: Session = Depends(get_db)):
    history = db.query(EquipmentMaintenance).filter(
        EquipmentMaintenance.equipment_id == equipment_id
    ).order_by(EquipmentMaintenance.maintenance_date.desc()).all()
    return history

# ============ TYPES ENDPOINT ============

@router.get("/types/list")
def get_equipment_types():
    return ["Motor", "Tractor", "Pump", "Generator", "Drip System", "Borewell", "Sprayer", "Vehicle"]