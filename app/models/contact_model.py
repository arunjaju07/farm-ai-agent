from sqlalchemy import Column, Integer, String, ForeignKey
from app.database.db import Base

class Contact(Base):
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    issue_type = Column(String, nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"))