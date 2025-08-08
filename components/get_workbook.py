import json
import os

import gspread
from google.oauth2.service_account import Credentials
import components.custom_error as customException

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, 'json', 'config.json')

try:
    with open(CONFIG_PATH, "r") as file:
        config = json.load(file)
except FileNotFoundError as e:
    raise customException.missingConfigJSON from None

def getWorkbook(workbookID):
    try:
        scopes = [
            config['scopes']
        ]
        creds = Credentials.from_service_account_file(CONFIG_PATH, scopes=scopes)

        client = gspread.authorize(creds)
        sheet_credential = workbookID
        workbook = client.open_by_key(sheet_credential)

        return workbook
    except KeyError as e:
        raise customException.missingField(e) from None