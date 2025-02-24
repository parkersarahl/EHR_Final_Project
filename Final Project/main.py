from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
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

#Secret Key (change to environment variable in production)
SECRET_KEY = 'your_secret_key'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

#Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Fake user database (replace with a real database)
fake_users_db = {
    "testuser": {
        "username": "testuser",
        "full_name": "Test User",
        "hashed_password": pwd_context.hash("password"),
        "disabled": False,
    }
}
# Function to verify password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Function to get user
def get_user(username: str):
    user = fake_users_db.get(username)
    return user if user else None
# Function to create access token
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.timezone.utc() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user["username"]}, expires_delta=access_token_expires)
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication")

    user = get_user(username)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return {"username": user["username"]}


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