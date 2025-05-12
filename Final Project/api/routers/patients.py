import json, requests
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Patient
from pydantic import BaseModel
from services.ehr.epic import EpicEHR, EPIC_FHIR_URL

router = APIRouter(prefix="/patients", tags=["patients"])

# Pydantic model
class PatientCreate(BaseModel):
    name: str
    dob: str

# Create a new patient
@router.post("/")
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    fhir_data = {
        "resourceType": "Patient",
        "name": [{"text": patient.name}],
        "birthDate": patient.dob
    }

    new_patient = Patient(
        name = patient.name,
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

@router.post("/fetch-epic-patient/{patient_id}")
def fetch_epic_patient(patient_id: str, db: Session = Depends(get_db)):
    access_token = EpicEHR.get_epic_token()

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{EPIC_FHIR_URL}/{patient_id}", headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch patient from Epic")

    fhir_data = response.json()
    name = fhir_data.get("name", [{}])[0].get("text", "Unknown")
    birth_date = fhir_data.get("birthDate", "1900-01-01")

    new_patient = Patient(name=name, dob=birth_date, fhir_json=json.dumps(fhir_data))
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    return {"message": "Patient fetched and stored", "fhir_data": fhir_data}
