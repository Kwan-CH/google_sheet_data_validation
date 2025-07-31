import json

import gspread
from google.oauth2.service_account import Credentials
import components.customError as customException

try:
    with open("json/config.json", "r") as file:
        config = json.load(file)
except FileNotFoundError as e:
    raise customException.missingConfigJSON from None

def getWorkbook(workbookID):
    try:
        scopes = [
            config['scopes']
        ]
        creds = Credentials.from_service_account_file("json/config.json", scopes=scopes)

        client = gspread.authorize(creds)
        sheet_credential = workbookID
        workbook = client.open_by_key(sheet_credential)

        return workbook
    except KeyError as e:
        raise customException.missingField(e) from None