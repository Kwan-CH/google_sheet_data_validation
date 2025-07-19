import json
import time

import gspread
from google.oauth2.service_account import Credentials

try:
    with open("json/config.json", "r") as file:
        config = json.load(file)
except FileNotFoundError:
    print("Please ensure that you have downloaded the JSON file from your service account, renamed as config.json and added into the json directory")

scopes = [
    config['scopes']
]
creds = Credentials.from_service_account_file("json/config.json", scopes=scopes)

client = gspread.authorize(creds)
sheet_credential = config["workbookID"]
workbook = client.open_by_key(sheet_credential)

sheet = workbook.worksheet(config["worksheetName"])
config["sheetID"] = sheet._properties['sheetId']

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
    print("column_rules.json has been created, please refer to readme.md to configure the json file")

try:
    with open("json/config.json", "w") as file:
        json.dump(config, file, indent=2)
except FileNotFoundError:
    print("Please ensure that you have downloaded the JSON file from your service account, renamed as config.json and added into the json directory")