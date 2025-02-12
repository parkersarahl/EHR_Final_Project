from fastapi import FastAPI, Depends, HTTPException
import requests
import json
from sqlalchemy.orm import Session 
from database import SessionLocal, engine
from models import Patient  

app = FastAPI()


# Create Tables
Patient.metadata.create_all(bind=engine)

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

#EPIC FHIR URL
EPIC_FHIR_URL = "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/Patient"

# Fetch Patient from Epic and Store in Database
@app.post("/fetch-epic-patient/{patient_id}")
def fetch_epic_patient(patient_id: str, db: Session = Depends(get_db)):
    response = requests.get(f"{EPIC_FHIR_URL}/{patient_id}")

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

# Get Stored Patient by ID
@app.get("/patients/{patient_id}")
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    return json.loads(patient.fhir_json)