# fastAPI_test.py
from tkinter import filedialog
import requests
import os

from core.validation import run_validation

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
            {"workbookID": "1oFeGwkrIQTqZ_vkk71xB2RI7zpApio3mw7319WuvEvM", "sheetID": "0", "sheetName": "Demo_Test_1"}
        ]
    }
    response = requests.post(f"{BASE_URL}/validate", json=payload)

def initialise_post():
    # This simulates duplicate keys in the body.
    # Note: JSON doesn't allow duplicate keys in a dict,
    # so you must use a list of dicts instead.
    payload = {
        "worksheets": [
            {"workbookID": "1u3kAQvKy9EiBCmi_OrL5W5poiwUgvY0uBx0K8c0-8iI", "sheetID": "0"}

        ]
    }
    response = requests.post(f"{BASE_URL}/initialize", json=payload)

def return_json_file():
    response = requests.get(f"{BASE_URL}/return-json")
    print(response.json())

DOWNLOAD_PATH = os.path.join(os.path.expanduser("~"), "Downloads")
JSON_FILE_PATH = "./worksheet_column"

def download_json_file(filename):
    SAVE_PATH = os.path.join(DOWNLOAD_PATH, filename)
    response = requests.get(f"{BASE_URL}/download-json?filename={filename}")
    if response.status_code == 200:
        with open(SAVE_PATH, "wb") as f:
            f.write(response.content)
    else:
        print(f"Error: {response.status_code} - {response.text}")

def upload_json_file():
    # Currently works only in Windows OS
    json_file_path = filedialog.askopenfilenames(title="Select JSON file")
    # json_file_path = filedialog.(title="Select JSON file")
    # if not json_file_path.endswith(".json"):
    #     print("Only .json files are allowed")
    #     return
    files = [("files", (open(path, "rb"))) for path in json_file_path]
    # with open(json_file_path, "rb") as f:
    #     files = {"file": (os.path.basename(json_file_path), f, "application/json")}
    response = requests.post(f"{BASE_URL}/upload-json", files=files)
    if response.status_code == 200:
        print("File uploaded successfully")
    else:
        print(f"Error: {response.status_code} - {response.text}")

# validate_get()

initialise_post()
# validate_post()
# return_json_file()
# download_json_file("sample.json")
# upload_json_file()