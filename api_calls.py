import requests
import json
from app import *


def validate_company_cui(cui):
    url = "https://api.openapi.ro/api/companies/" + cui
    headers = {"content-type": "application/json", "x-api-key": open_api_key}
    if requests.get(url, headers=headers).status_code == 200:
        return True
    else:
        return False


def validate_person_cnp(cnp):
    url = "https://api.openapi.ro/api/validate/cnp/" + cnp
    headers = {"content-type": "application/json", "x-api-key": open_api_key}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        if response.json()["valid"]:
            return True
        else:
            return False
    else:
        return False

