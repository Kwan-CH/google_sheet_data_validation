import json

import components.customError as customException
from components.getWorkbook import getWorkbook

try:
    with open("json/config.json", "r") as file:
        config = json.load(file)

        workbook = getWorkbook()
        sheet = workbook.worksheet(config["worksheetName"])
        config["sheetID"] = sheet._properties['sheetId']

        records = sheet.get_all_values()
        for record in records:
            if "#" in record[0]:
                pass
            else:
                header_idx = records.index(record)
                config["headerIndex"] = header_idx
                break
    with open("json/config.json", "w") as file:
        json.dump(config, file, indent=2)
except FileNotFoundError as e:
    raise customException.missingConfigJSON from None


def write_column_rule(action, name):
    headers = records[header_idx]  # your original header list
    headers_json = {
        header: {
            "rule": "",
            "param": ""
        }
        for header in headers
    }
    if action == "create":
        with open(f"json/{name}.json", "x") as file:
            json.dump(headers_json, file, indent=4)
    else:
        with open(f"json/{name}.json", "w") as file:
            json.dump(headers_json, file, indent=4)


while True:
    try:
        choice = int(input("\nAre you...\n"
                           "1: working on a new worksheet? \n\t- A new json file will be created\n"
                           "2: modifying existing worksheet? \n\t- Be advice that existing rule will be cleared make sure to have a backup beforehand\n"
                           "Please enter a choice: "))
        if choice == 1:
            name = input("\nPlease enter the name for the json file \n\t** no need to include .json extension\nName: ")
            write_column_rule("create", name)
            break
        elif choice == 2:
            name = input("\nPlease enter the name of the json file \n\t** no need to include .json extension\nName: ")
            write_column_rule("modify", name)
            break
        else:
            print("\nPlease only select 1 or 2")
    except ValueError:
        print("Please enter digits only!!!")

print("Sheet\'s column have been retrieved...")

print("Please configure the rules to be applied for the column, then run the main.py to start the validation")
# main()