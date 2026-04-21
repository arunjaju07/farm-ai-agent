from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
import os

router = APIRouter(prefix="/zones", tags=["Zones"])

class ZoneCreate(BaseModel):
    name: str
    area_acres: Optional[float] = None
    location_id: int

# Add a new zone
@router.post("/add")
def add_zone(zone: ZoneCreate):
    # Get database path
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "farm.db")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if location exists
        cursor.execute("SELECT id FROM locations WHERE id = ?", (zone.location_id,))
        if not cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=404, detail="Location not found")
        
        # Insert zone
        cursor.execute(
            "INSERT INTO zones (name, area_acres, location_id) VALUES (?, ?, ?)",
            (zone.name, zone.area_acres, zone.location_id)
        )
        conn.commit()
        zone_id = cursor.lastrowid
        conn.close()
        
        return {"message": "Zone added successfully", "zone_id": zone_id}
    
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))

# Get all zones
@router.get("/all")
def get_all_zones():
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "farm.db")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, area_acres, location_id, created_at FROM zones")
    zones = cursor.fetchall()
    conn.close()
    
    return [
        {
            "id": z[0],
            "name": z[1],
            "area_acres": z[2],
            "location_id": z[3],
            "created_at": z[4]
        }
        for z in zones
    ]

# Update zone
@router.put("/update/{zone_id}")
def update_zone(zone_id: int, zone: ZoneCreate):
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "farm.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE zones SET name = ?, area_acres = ?, location_id = ? WHERE id = ?",
        (zone.name, zone.area_acres, zone.location_id, zone_id)
    )
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    
    if affected == 0:
        raise HTTPException(status_code=404, detail="Zone not found")
    return {"message": "Zone updated successfully"}

# Delete zone
@router.delete("/delete/{zone_id}")
def delete_zone(zone_id: int):
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "farm.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if zone exists
    cursor.execute("SELECT id FROM zones WHERE id = ?", (zone_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Zone not found")
    
    # Delete zone
    cursor.execute("DELETE FROM zones WHERE id = ?", (zone_id,))
    conn.commit()
    conn.close()
    
    return {"message": "Zone deleted successfully"}

# Get zones by location
@router.get("/location/{location_id}")
def get_zones_by_location(location_id: int):
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "farm.db")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, area_acres, location_id, created_at FROM zones WHERE location_id = ?",
        (location_id,)
    )
    zones = cursor.fetchall()
    conn.close()
    
    return [
        {
            "id": z[0],
            "name": z[1],
            "area_acres": z[2],
            "location_id": z[3],
            "created_at": z[4]
        }
        for z in zones
    ]