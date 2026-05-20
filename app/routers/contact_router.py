from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database.db import SessionLocal
from app.models.contact_model import Contact

router = APIRouter(prefix="/contacts", tags=["Contacts"])

class ContactCreate(BaseModel):
    name: str
    phone: str
    issue_type: str
    location_id: int

@router.post("/add")
def create_contact(contact: ContactCreate):
    db = SessionLocal()
    
    try:
        new_contact = Contact(
            name=contact.name,
            phone=contact.phone,
            issue_type=contact.issue_type,
            location_id=contact.location_id
        )
        db.add(new_contact)
        db.commit()
        db.refresh(new_contact)
        db.close()
        
        return {"message": "Contact added successfully", "contact_id": new_contact.id}
    except Exception as e:
        db.close()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/all")
def get_all_contacts():
    db = SessionLocal()
    contacts = db.query(Contact).all()
    db.close()
    return contacts

@router.get("/all")
def get_all_contacts():
    db = SessionLocal()
    contacts = db.query(Contact).all()
    db.close()
    return contacts

@router.get("/{contact_id}")
def get_contact(contact_id: int):
    db = SessionLocal()
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    db.close()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@router.put("/update/{contact_id}")
def update_contact(contact_id: int, contact: ContactCreate):
    db = SessionLocal()
    existing = db.query(Contact).filter(Contact.id == contact_id).first()
    if not existing:
        db.close()
        raise HTTPException(status_code=404, detail="Contact not found")
    
    existing.name = contact.name
    existing.phone = contact.phone
    existing.issue_type = contact.issue_type
    existing.location_id = contact.location_id
    
    db.commit()
    db.close()
    return {"message": "Contact updated successfully"}

@router.delete("/delete/{contact_id}")
def delete_contact(contact_id: int):
    db = SessionLocal()
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        db.close()
        raise HTTPException(status_code=404, detail="Contact not found")
    
    db.delete(contact)
    db.commit()
    db.close()
    return {"message": "Contact deleted successfully"}