from functools import partial
import pandas as pd
import json
import glob
import os

from components import clear_formatting
from components import error_logging
from components.custom_error import unrecognizedRule
from components.get_workbook import getWorkbook
from components.sort_location import sort_error_list
from components.data_validator import Validator
from components.structure_validator import correctFormat

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
JSON_DIR = os.path.join(BASE_DIR, 'json')

with open(os.path.join(JSON_DIR, "checkMap.json"), "r") as file:
    rule_map = json.load(file)[0].get("Available")

def highlightError(workbookID, sheetID, df, sorted_errors, headerIndex, column_rules):
    workbook = getWorkbook(workbookID)
    sheet = workbook.get_worksheet_by_id(sheetID)
    if len(sorted_errors) == 0:
        clear_formatting.clear_format(workbook, sheetID, list(column_rules.keys()), df, headerIndex)
        error_logging.log_error(workbook, sheet.title, "No error found, thank you for your cooperation")
        return 200, "No error found, can proceed to the next step...."
    else:
        clear_formatting.clear_format(workbook, sheetID, list(column_rules.keys()), df, headerIndex)
        error_logging.highlight_error(workbook, sheetID, sorted_errors)
        error_logging.log_error(workbook, sheet.title, sorted_errors)
        return 200, "Validation rules has been applied the error has logged, please check"

def formatCheck(headers, column_rules):
    correctFormat = True
    for header in headers:
        if header.strip() in column_rules.keys():
            pass
        else:
            correctFormat = False
            break
    return correctFormat

# def init_validation(sheetName: str)
# Check if isInOption's "option" is dict and can be found in the same folder
# Details will be stored as a dict
# {"fileName": "xxx", "columnName", "yyy"}
def init_validation(sheetName: str):
    pass

# def prepare_validation(details: dict, sheetName: str)
# details Parameter contains workbookID, sheetID, columnName
# Read the specified Google Sheet file and return the header(s) column data as list
# Prepare the valid options specified in isInOption's dict, and return a dict "rules", modified from the original JSON file in runtime
# for run_validation
def prepare_validation(details: dict, sheetName: str):
    pass

# Change to accept "rules" as dict parameter
# Run init_validation and prepare_validation before the validation process
def run_validation(workbookID, sheetID, sheetName):
    WORKSHEET_DIR = os.path.join(BASE_DIR, "worksheet_column")
    file_name = glob.glob(f'{WORKSHEET_DIR}/*{sheetName}*')

    if not file_name:
        return {"code": 404, "message": "The corresponding column rules json file haven't been create, please create and configure it now"}
    else:
        with open(file_name[0], "r") as file:
            # ---------------------------------
            # Will be modified if JSON structure changes
            data = json.load(file)[0]
            column_rules = data["rules"]
            headers_order = data["structure"]["columns"]
            # ---------------------------------

        workbook = getWorkbook(workbookID)
        sheet = workbook.get_worksheet_by_id(sheetID)
        records = sheet.get_all_values()
        header_idx = 0

        for record in records:
            if "#" in record[0]:
                pass
            else:
                header_idx = records.index(record)
                break
        correctFormatResponse = correctFormat(sheet, records[header_idx], column_rules, headers_order)
        if correctFormatResponse.get("status"):
            data = records[header_idx + 1:]

            df = pd.DataFrame(data, columns=column_rules.keys())
            checker = Validator(df, header_idx)

            for column, ruleParam in column_rules.items():
                rule = ruleParam.get("rule")
                param = ruleParam.get("param")
                if rule.strip() == "":
                    pass
                elif rule not in list(rule_map.keys()):
                    raise unrecognizedRule(rule)
                else:
                    flatten = {
                        "column_name": column,
                        **param
                    }
                    func = getattr(checker, rule)
                    wrapper = partial(func, **flatten)
                    wrapper()

            sorted_errors = sort_error_list(checker.error_log)
            code, message = highlightError(workbookID, sheetID, df, sorted_errors, header_idx, column_rules)
            return {"code": code, "message": message}
        else:
            error_logging.log_error(workbook, sheet.title, correctFormatResponse['message'] + "\nKindly revert the changes that you have made")
            return {"code": 400, "message": correctFormatResponse.get("message") + "\nKindly revert the changes that you have made"}