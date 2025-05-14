
import os
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env

EPIC_CLIENT_ID = os.getenv("EPIC_CLIENT_ID")
EPIC_REDIRECT_URI = os.getenv("EPIC_REDIRECT_URI")
EPIC_AUTH_URL = "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/authorize"
EPIC_TOKEN_URL = "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token"
EPIC_SCOPES = "openid profile user/*.read patient/*.read offline_access"
EPIC_PRIVATE_KEY = os.getenv("EPIC_PRIVATE_KEY")

EPIC_ISSUER = EPIC_CLIENT_ID  # usually the client ID
EPIC_AUDIENCE = EPIC_TOKEN_URL
