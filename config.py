import json
import time

import gspread
from google.oauth2.service_account import Credentials

import components.customError as customException

try:
    with open("json/config.json", "r") as file:
        config = json.load(file)
except FileNotFoundError as e:
    raise customException.missingConfigJSON from None

try:
    scopes = [
        config['scopes']
    ]
    creds = Credentials.from_service_account_file("json/config.json", scopes=scopes)

    client = gspread.authorize(creds)
    sheet_credential = config["workbookID"]
    workbook = client.open_by_key(sheet_credential)

    sheet = workbook.worksheet(config["worksheetName"])
    config["sheetID"] = sheet._properties['sheetId']
    with open("json/config.json", "w") as file:
        json.dump(config, file, indent=2)
except KeyError as e:
    raise customException.missingField(e) from None

records = sheet.get_all_values()
headers = records[0]
rows = records[1:]

headers_json = dict.fromkeys(headers, "")

print("Sheet\'s column have been retrieved...")
time.sleep(3)

try:
    with open("json/column_rules.json", "r") as file:
        file.read()
except FileNotFoundError:
    print("column_rules.json file is being created...")
    time.sleep(3)
    open("json/column_rules.json", "x")
finally:
    with open("json/column_rules.json", "w") as file:
        json.dump(headers_json, file, indent=4)

try:
    with open("json/data.json", "r") as file:
        file.read()
except FileNotFoundError:
    open("json/data.json", "x")
finally:
    with open("json/data.json", "w") as file:
        json.dump(rows, file, indent=2)
    print("column_rules.json has been created, it is stored at the folder called json, please refer to readme.md to configure that json file")