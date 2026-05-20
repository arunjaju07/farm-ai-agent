from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.database.db import SessionLocal
from app.models.zone_model import Zone

router = APIRouter(prefix="/zones", tags=["Zones"])

class ZoneCreate(BaseModel):
    name: str
    area_acres: float = 0
    location_id: int

@router.post("/add")
def add_zone(zone: ZoneCreate):
    db = SessionLocal()
    
    try:
        new_zone = Zone(
            name=zone.name,
            area_acres=zone.area_acres,
            location_id=zone.location_id
        )
        db.add(new_zone)
        db.commit()
        db.refresh(new_zone)
        db.close()
        
        return {"message": "Zone added successfully", "zone_id": new_zone.id}
    
    except Exception as e:
        db.close()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/all")
def get_all_zones():
    db = SessionLocal()
    zones = db.query(Zone).all()
    db.close()
    
    return [
        {
            "id": z.id,
            "name": z.name,
            "area_acres": z.area_acres,
            "location_id": z.location_id,
            "created_at": z.created_at
        }
        for z in zones
    ]

@router.get("/location/{location_id}")
def get_zones_by_location(location_id: int):
    db = SessionLocal()
    zones = db.query(Zone).filter(Zone.location_id == location_id).all()
    db.close()
    return zones

@router.put("/update/{zone_id}")
def update_zone(zone_id: int, zone: ZoneCreate):
    db = SessionLocal()
    
    try:
        existing_zone = db.query(Zone).filter(Zone.id == zone_id).first()
        if not existing_zone:
            db.close()
            raise HTTPException(status_code=404, detail="Zone not found")
        
        existing_zone.name = zone.name
        existing_zone.area_acres = zone.area_acres
        existing_zone.location_id = zone.location_id
        
        db.commit()
        db.close()
        
        return {"message": "Zone updated successfully"}
    
    except Exception as e:
        db.close()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete/{zone_id}")
def delete_zone(zone_id: int):
    db = SessionLocal()
    
    try:
        zone = db.query(Zone).filter(Zone.id == zone_id).first()
        if not zone:
            db.close()
            raise HTTPException(status_code=404, detail="Zone not found")
        
        db.delete(zone)
        db.commit()
        db.close()
        
        return {"message": "Zone deleted successfully"}
    
    except Exception as e:
        db.close()
        raise HTTPException(status_code=500, detail=str(e))