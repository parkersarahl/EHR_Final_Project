# services/ehr/epic.py
from .base import EHRVendor
from datetime import datetime, timezone, timedelta
import jwt, os, uuid, requests, json
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.x509 import load_pem_x509_certificate


EPIC_FHIR_URL = "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4"

CLIENT_ID = "b3d4de6f-fff6-45cb-ad65-eff1c502c2c1"  
EPIC_TOKEN_URL = "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token"
PRIVATE_KEY_PATH = "./api/keys/epic-on-fhir-private-key.pem"
PUBLIC_CERT_PATH = "./api/keys/epic-on-fhir-public-key-509.pem"

class EpicEHR(EHRVendor):
    @staticmethod
    def get_epic_token():
        # load key pair created by following https://fhir.epic.com/Documentation?docId=oauth2&section=Creating-Key-Pair
        os.chdir("C:/Users/sarah/UTC/EHR_Final_Project/Final Project")

        # Load the private key
        with open(PRIVATE_KEY_PATH, 'rb') as private_key_file:
            private_key = load_pem_private_key(private_key_file.read(), None, default_backend())

        #Validate by loading public key. This is optional but recommended to ensure the private key matches the public key
        with open(PUBLIC_CERT_PATH, 'rb') as cert_file:
            cert_obj = load_pem_x509_certificate(cert_file.read(), backend=default_backend())
            public_key = cert_obj.public_key()

        # build the JWT
        endpoint = "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token"
        now = datetime.now(tz=timezone.utc)
        exp_time = int((now + timedelta(minutes=5)).timestamp())
        payload = {
            "iss": CLIENT_ID,
            "sub": CLIENT_ID,
            "aud": endpoint,
            "jti": str(uuid.uuid4()),
            "exp": exp_time,
        }
        # Encode the JWT using RS384 algorithm
        token = jwt.encode(
            payload, 
            private_key, 
            algorithm="RS384",
            headers={"alg": "RS384", "typ": "JWT"}
        )
        
        payload = {
            "grant_type": "client_credentials",
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": token,
            
            "scope": "system/DocumentReference.rs system/Observation.rs system/Patient.rs"
  # Optional: specify scopes if needed
        }
        # Request access token
        response = requests.post(
            EPIC_TOKEN_URL,
            data=payload
        )
        if response.status_code != 200:
            raise Exception(f"Failed to get token: {response.status_code}, {response.text}")

        token_response = response.json()
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        print(decoded_token)

        print("Full token response:", response.status_code, response.text)

        if "scope" in token_response:
            print("Granted scopes:", token_response["scope"])
        else:
         print("No scope information found in the token response.")

        return response.json()["access_token"]
    
    @staticmethod
    def find_patient_by_name(family_name: str, given_name: str = None, birthdate: str = None, access_token: str = None, return_id_only: bool = False):
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/fhir+json",
        }
        
        params = {}
        if family_name:
            params["family"] = family_name
        if given_name:
            params["given"] = given_name
        if birthdate:
            params["birthdate"] = birthdate

        response = requests.get(f"{EPIC_FHIR_URL}/Patient", headers=headers, params=params)
        
        if response.status_code != 200:
            raise Exception(f"Failed to search patient: {response.status_code}, {response.text}")

        bundle = response.json()
        print(json.dumps(response.json(), indent=2))

        patients = []

        if "entry" in bundle:
            for entry in bundle["entry"]:
                resource = entry.get("resource", {})
                if resource.get("resourceType") == "Patient":
                    if return_id_only:
                        # If only ID is needed, return it directly
                        return resource.get("id")
                    # Build a clean patient object
                    patient_info = {
                        "id": resource.get("id"),
                        "name": resource["name"][0].get("text", "Unknown") if "name" in resource else "Unknown",
                        "birthDate": resource.get("birthDate", "Unknown")
                    }
            
                    patients.append(patient_info)
                    

        return patients
    
    