# routers/auth.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from utils.auth import verify_password, create_access_token, hash_password, ACCESS_TOKEN_EXPIRE_MINUTES 

#Test User for Epic EHR
fake_users_db = {
    "FHIRTWO": {
        "username": "FHIRTWO",
        "full_name": "FHIRTWO, USER",
        "hashed_password": hash_password("EpicFhir11!"),  # You can pre-hash or move this out
        "disabled": False,
    }
}

def get_user(username: str):
    return fake_users_db.get(username)

router = APIRouter()

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(form_data.username)
    
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from fastapi import status
from fastapi import Request

# These should match what's in utils.auth
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.get("/users/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication",
        )

    user = get_user(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return {"username": user["username"]}
