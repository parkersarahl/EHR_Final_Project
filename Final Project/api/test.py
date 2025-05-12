from services.ehr.epic import EpicEHR

token = EpicEHR.get_epic_token()
#print("Access Token:", token)

from services.ehr.epic import EpicEHR

#EpicEHR.test_fetch_patient_list()

patient_bundle = EpicEHR.find_patient_by_name(family_name="Lopez", birthdate="1987-09-12", access_token=token)

print("Patient Bundle:", patient_bundle)