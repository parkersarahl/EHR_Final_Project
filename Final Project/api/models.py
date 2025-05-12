from sqlalchemy import Column, Integer, String, Text, Date
from database import Base  # Import Base from database.py

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    last_name = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    dob = Column(Date, nullable=False)
    fhir_json = Column(Text, nullable=False)
