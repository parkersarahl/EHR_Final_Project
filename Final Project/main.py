from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Text, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import json

app = FastAPI()

# Database Configuration
DATABASE_URL = "postgresql://postgres:Carol2024#@localhost/healthcare_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define Patient Model
class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    dob = Column(Date, nullable=False)
    fhir_json = Column(Text, nullable=False)

# Create Tables
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create Patient Endpoint
@app.post("/patients/")
def create_patient(name: str, dob: str, db: Session = Depends(get_db)):
    fhir_data = {
        "resourceType": "Patient",
        "name": [{"text": name}],
        "birthDate": dob
    }

    new_patient = Patient(name=name, dob=dob, fhir_json=json.dumps(fhir_data))
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    return {"message": "Patient created successfully", "fhir_data": fhir_data}

# Get Patient by ID
@app.get("/patients/{patient_id}")
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    return json.loads(patient.fhir_json)
