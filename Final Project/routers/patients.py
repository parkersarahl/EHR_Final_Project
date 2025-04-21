from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Patient
from pydantic import BaseModel
import json

router = APIRouter(prefix="/patients", tags=["patients"])

# Pydantic model
class PatientCreate(BaseModel):
    last_name: str
    first_name: str 
    dob: str

# Create a new patient
@router.post("/")
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    fhir_data = {
        "resourceType": "Patient",
        "name": [{"text": patient.first_name + " " + patient.last_name}],
        "birthDate": patient.dob
    }

    new_patient = Patient(
        last_name=patient.last_name,
        first_name=patient.first_name,
        dob=patient.dob,
        fhir_json=json.dumps(fhir_data)
    )
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    return {
        "message": "Patient created successfully",
        "patient_id": new_patient.id,
        "fhir_data": fhir_data
    }

# Fetch patient by last name
@router.get("/search")
def search_patients(last_name: str, db: Session = Depends(get_db)):
    matches = db.query(Patient).filter(Patient.last_name.ilike(f"%{last_name}%")).all()
    if not matches:
        raise HTTPException(status_code=404, detail="No patients found")

    return [
        {
            "id": patient.id,
            "name": patient.last_name + " " + patient.first_name,
            "dob": patient.dob
        }
        for patient in matches
    ]

# Fetch a specific patient by ID
@router.get("/{patient_id}")
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    return json.loads(patient.fhir_json)

#Delete a patient by ID
@router.delete("/{patient_id}")
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    db.delete(patient)
    db.commit()

    return {"message": "Patient deleted successfully"}

