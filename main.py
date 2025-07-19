import pandas as pd
import json

from components.validator import Validator
from components import error_logging, clear_formatting
from components.customError import unrecognizedRule

def highlightError():
    print("All data has been validated, below are the errors found")
    sorted_errors = sorted(checker.error_log, key=lambda x: x['location'])
    for error in sorted_errors:
        print(error)

    print("Error will be highlight now, and the error will be log in another sheet")

    import gspread
    from google.oauth2.service_account import Credentials
    scopes = [
        config['scopes']
    ]
    creds = Credentials.from_service_account_file("json/config.json", scopes=scopes)

    client = gspread.authorize(creds)
    sheet_credential = config["workbookID"]
    workbook = client.open_by_key(sheet_credential)

    clear_formatting.clear_format(workbook, config["sheetID"], list(column_rules.keys()), df)
    error_logging.highlight_error(workbook, config["sheetID"], sorted_errors)
    error_logging.log_error(workbook, sorted_errors)

with open("json/config.json", "r") as file:
    config = json.load(file)

with open("json/checkMap.json", "r") as file:
    rule_map = json.load(file)

with open("json/column_rules.json", "r") as file:
    column_rules = json.load(file)

with open("json/data.json", "r") as file:
    rows = json.load(file)

df = pd.DataFrame(rows, columns=list(column_rules.keys()))
checker = Validator(df)

try:
    for idx, row in df.iterrows():
        for column, rule in column_rules.items():
            param_flag = False
            if not rule:
                continue  # skip empty

            if ":" in rule:
                param_flag = True
                rule, param = rule.split(":")
                if ", " in param:
                    param = [opt.strip() for opt in param.split(",")]

            mapped = rule_map[rule]

            if mapped == "":
                pass  # skip if rule not found in map
            else:
                method = getattr(checker, rule_map.get(rule))
                if param_flag:
                    method(row, column, param)
                else:
                    method(row, column)
    highlightError()
except KeyError as e:
    raise unrecognizedRule(e) from None