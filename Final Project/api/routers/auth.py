# routers/auth.py

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
import urllib.parse
import httpx


from config import (
    EPIC_CLIENT_ID,
    EPIC_REDIRECT_URI,
    EPIC_AUTH_URL,
    EPIC_SCOPES,
)
from utils.auth import exchange_code_for_token

router = APIRouter()


@router.get("/login")
async def login_to_epic():
    query = urllib.parse.urlencode({
        "response_type": "code",
        "client_id": EPIC_CLIENT_ID,
        "redirect_uri": EPIC_REDIRECT_URI,
        "scope": EPIC_SCOPES,
        "state": "secure_random_state",  # Replace with a secure random state
    })
    return RedirectResponse(f"{EPIC_AUTH_URL}?{query}")

@router.get("/auth/callback")
async def auth_callback(request: Request):
    code = request.query_params.get("code")

    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI,
                "client_id": CLIENT_ID,
                # If you're using JWT client auth, add client_assertion here
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    token_response = response.json()
    if "access_token" not in token_response:
        raise HTTPException(status_code=400, detail="Token exchange failed")

    return token_response
