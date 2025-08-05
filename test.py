# fastAPI_test.py
import requests

from core.main import run_validation

BASE_URL = "http://localhost:8000"

def validate_get():
    params = {
        "sheetId": "123",
        # This simulates multiple `sheetName` values:
        "sheetName": ["SheetA", "SheetB", "SheetC"]
    }
    response = requests.get(f"{BASE_URL}/validate", params=params)
    print("GET Response:")
    print(response.status_code)
    print(response.json())

def validate_post():
    # This simulates duplicate keys in the body.
    # Note: JSON doesn't allow duplicate keys in a dict,
    # so you must use a list of dicts instead.
    payload = {
        "worksheets": [
            {"workbookID": "1AztVEyWwm9akIkmy8lmwEpJQ5k1loslYznnWYxW4aWU", "sheetID": "0", "sheetName": "Demo_Test"}
        ]
    }
    response = requests.post(f"{BASE_URL}/validate", json=payload)
    print(response)

def initialise_post():
    # This simulates duplicate keys in the body.
    # Note: JSON doesn't allow duplicate keys in a dict,
    # so you must use a list of dicts instead.
    payload = {
        "worksheets": [
            {"workbookID": "1AztVEyWwm9akIkmy8lmwEpJQ5k1loslYznnWYxW4aWU", "sheetID": "0"}

        ]
    }
    response = requests.post(f"{BASE_URL}/initialize", json=payload)

# validate_get()

# initialise_post()
validate_post()

