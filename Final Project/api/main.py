from getpass import getuser
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from utils.auth import (
    verify_password,
    create_access_token,
    decode_access_token,
    hash_password  
)

from database import  engine
from models import Patient  
from routers import patients, auth
from routers.epic import router as epic_router


app = FastAPI()

# Enable CORS for your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust if deployed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Include your router
#app.include_router(epic_router, prefix="/api")  # optional: prefix all routes

# Create Tables
Patient.metadata.create_all(bind=engine)

#Register the router
app.include_router(patients.router)
app.include_router(auth.router)
app.include_router(epic_router, prefix="/api")  # optional: prefix all routes

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

