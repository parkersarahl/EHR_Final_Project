from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Patient
from pydantic import BaseModel
import json

router = APIRouter(prefix="/patients", tags=["patients"])

# Pydantic model
class PatientCreate(BaseModel):
    name: str
    dob: str

@router.post("/")
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    fhir_data = {
        "resourceType": "Patient",
        "name": [{"text": patient.name}],
        "birthDate": patient.dob
    }

    new_patient = Patient(
        name=patient.name,
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

@router.get("/search")
def search_patients(last_name: str, db: Session = Depends(get_db)):
    matches = db.query(Patient).filter(Patient.name.ilike(f"%{last_name}%")).all()
    if not matches:
        raise HTTPException(status_code=404, detail="No patients found")

    return [
        {
            "id": patient.id,
            "name": patient.name,
            "dob": patient.dob
        }
        for patient in matches
    ]

@router.get("/{patient_id}")
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    return json.loads(patient.fhir_json)
