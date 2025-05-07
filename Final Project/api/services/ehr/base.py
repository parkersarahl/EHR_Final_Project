# services/ehr/base.py
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session

class EHRVendor(ABC):
    @abstractmethod
    def fetch_patient(self, patient_id: str, db: Session):
        pass
