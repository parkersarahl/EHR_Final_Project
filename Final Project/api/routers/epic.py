# routes/epic.py
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from services.ehr.epic import EpicEHR  # adjust import paths as needed

router = APIRouter()

@router.get("/epic/patients", summary="Search patients by name")
def search_patients(
    family_name: str = Query(..., description="Patient's last name"),
    given_name: str = Query(None, description="Patient's first name"),
    birthdate: str = Query(None, description="Patient's birthdate in YYYY-MM-DD format"),
):
    try:
         # 🔍 Strip whitespace to ensure clean query values
        family_name = family_name.strip()
        given_name = given_name.strip() if given_name else None
        birthdate = birthdate.strip() if birthdate else None

        token = EpicEHR.get_epic_token()
        patients = EpicEHR.find_patient_by_name(
            family_name=family_name,
            given_name=given_name,
            birthdate=birthdate,
            access_token=token
        )
       

        return {"results": patients}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))