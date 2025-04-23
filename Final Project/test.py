from services.ehr.epic import get_epic_token

token = get_epic_token()
print("Access Token:", token)

from services.ehr.epic import EpicEHR

EpicEHR.test_fetch_patient_list()