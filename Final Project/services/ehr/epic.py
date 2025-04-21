# services/ehr/epic.py
import requests, json
from models import Patient
from .base import EHRVendor

EPIC_FHIR_URL = "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/Patient"

class EpicEHR(EHRVendor):
    def fetch_patient(self, patient_id: str, db):
        response = requests.get(f"{EPIC_FHIR_URL}/{patient_id}")
        if response.status_code != 200:
            return None

        fhir_data = response.json()
        name = fhir_data.get("name", [{}])[0].get("text", "Unknown")
        birth_date = fhir_data.get("birthDate", "1900-01-01")

        patient = Patient(name=name, dob=birth_date, fhir_json=json.dumps(fhir_data))
        db.add(patient)
        db.commit()
        db.refresh(patient)

        return patient
