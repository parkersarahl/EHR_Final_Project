from sqlalchemy import create_engine, Column, Integer, String, Text, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json

# Database Configuration
DATABASE_URL = "postgresql://postgres:Carol2024#@localhost/healthcare_db"

# Create Engine
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
def create_tables():
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully!")

# Insert Sample Data
def insert_sample_data():
    session = SessionLocal()
    fhir_data = {
        "resourceType": "Patient",
        "name": [{"text": "John Doe"}],
        "birthDate": "1980-01-01"
    }
    
    new_patient = Patient(name="John Doe", dob="1980-01-01", fhir_json=json.dumps(fhir_data))
    session.add(new_patient)
    session.commit()
    session.close()
    print("✅ Sample patient inserted!")

# Retrieve Patient by ID
def get_patient(patient_id):
    session = SessionLocal()
    patient = session.query(Patient).filter(Patient.id == patient_id).first()
    session.close()
    if patient:
        return json.loads(patient.fhir_json)
    return None

# Run Setup
if __name__ == "__main__":
    create_tables()
    insert_sample_data()

    # Fetch and Print Patient
    patient_data = get_patient(1)
    print(f"🔹 Retrieved Patient Data: {patient_data}")
