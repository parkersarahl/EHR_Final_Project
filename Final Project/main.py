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
from routers import patients, auth


app = FastAPI()

# Create Tables
Patient.metadata.create_all(bind=engine)

#Register the router
app.include_router(patients.router)
app.include_router(auth.router)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.get("/users/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid authentication")

    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid authentication")

    user = getuser(username)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return {"username": user["username"]}


