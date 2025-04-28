# services/ehr/epic.py
from models import Patient
from .base import EHRVendor
from datetime import datetime, timezone, timedelta
import jwt, os, uuid, requests, json
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.x509 import load_pem_x509_certificate


EPIC_FHIR_URL = "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4"

CLIENT_ID = "b3d4de6f-fff6-45cb-ad65-eff1c502c2c1"  
EPIC_TOKEN_URL = "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token"
PRIVATE_KEY_PATH = "keys/epic-on-fhir-private-key.pem"
PUBLIC_CERT_PATH = "keys/epic-on-fhir-public-key-509.pem"
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
    payload = {
        "iss": CLIENT_ID,
        "sub": CLIENT_ID,
        "aud": endpoint,
        "jti": str(uuid.uuid4()),
        "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=+1),
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
        "scope": "system/Patient/*.read"  # Optional: specify scopes if needed
    }
      # Request access token
    response = requests.post(
        EPIC_TOKEN_URL,
        data=payload
    )
    if response.status_code != 200:
        raise Exception(f"Failed to get token: {response.status_code}, {response.text}")

    return response.json()["access_token"]

class EpicEHR(EHRVendor):
    def fetch_patient(self, patient_id: str, db):
        token = get_epic_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/fhir+json"
        }

        response = requests.get(f"{EPIC_FHIR_URL}/{patient_id}", headers=headers)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch from Epic: {response.status_code} - {response.text}")

        fhir_data = response.json()
        name = fhir_data.get("name", [{}])[0].get("text", "Unknown")
        birth_date = fhir_data.get("birthDate", "1900-01-01")

        patient = Patient(
            last_name=name.split()[-1],
            first_name=" ".join(name.split()[:-1]),
            dob=birth_date,
            fhir_json=json.dumps(fhir_data)
        )
        db.add(patient)
        db.commit()
        db.refresh(patient)

        return patient
    
    def find_patient_by_name(family_name: str, given_name: str = None, birthdate: str = None, access_token: str = None):
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/fhir+json",
        }
        
        params = {"family": family_name}
        if given_name:
            params["given"] = given_name
        if birthdate:
            params["birthdate"] = birthdate

        response = requests.get(f"{EPIC_FHIR_URL}/Patient", headers=headers, params=params)
        
        if response.status_code != 200:
            raise Exception(f"Failed to search patient: {response.status_code}, {response.text}")

        bundle = response.json()

        patients = []

        if "entry" in bundle:
            for entry in bundle["entry"]:
                resource = entry.get("resource", {})
                if resource.get("resourceType") == "Patient":
                    # Build a clean patient object
                    patient_info = {
                        "id": resource.get("id"),
                        "name": resource["name"][0].get("text", "Unknown") if "name" in resource else "Unknown",
                        "birthDate": resource.get("birthDate", "Unknown")
                    }
                    patients.append(patient_info)

        if not patients:
            print("No matching patients found.")
        else:
            for patient in patients:
                print(f"Found Patient: {patient['name']} (ID: {patient['id']}, BirthDate: {patient['birthDate']})")

        return patients

    @staticmethod
    def test_fetch_patient_list():
        token = get_epic_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/fhir+json"
        }
        params = {
            "family": "Lopez",
            "birthdate": "1987-09-12"
        }
        response = requests.get(f"{EPIC_FHIR_URL}/Patient", headers=headers, params=params)
       

        if response.status_code != 200:
            raise Exception(f"Failed to fetch patient list: {response.status_code}, {response.text}")
        
        data = response.json()
        patient_entry = response.json()["entry"][0]["resource"]

        print(f"Name: {patient_entry['name'][0]['text']}")
        print(f"Gender: {patient_entry['gender']}")
        print(f"DOB: {patient_entry['birthDate']}")
        print(f"Email: {patient_entry['telecom'][3]['value']}")
        print(f"Primary Address: {', '.join(patient_entry['address'][0]['line'])}, {patient_entry['address'][0]['city']}, {patient_entry['address'][0]['state']} {patient_entry['address'][0]['postalCode']}")

        return data
