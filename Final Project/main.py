from getpass import getuser
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from utils.auth import (
    verify_password,
    create_access_token,
    decode_access_token,
    hash_password  
)

from database import  engine
from models import Patient  
from routers import patients, auth, epic


app = FastAPI()

# Create Tables
Patient.metadata.create_all(bind=engine)

#Register the router
app.include_router(patients.router)
app.include_router(auth.router)
app.include_router(epic.router)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

