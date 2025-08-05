from functools import partial
import pandas as pd
import json
import glob
import os

from components import clear_formatting
from components import error_logging
from components.customError import unrecognizedRule
from components.getWorkbook import getWorkbook
from components.sort_location import sort_error_list
from components.validator import Validator

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
JSON_DIR = os.path.join(BASE_DIR, 'json')

with open(os.path.join(JSON_DIR, "config.json"), "r") as file:
    config = json.load(file)

with open(os.path.join(JSON_DIR, "checkMap.json"), "r") as file:
    rule_map = json.load(file)

def highlightError(workbookID, sheetID, df, sorted_errors, headerIndex, column_rules):
    # print("All data has been validated, below are the errors found")
    # # for error in sorted_errors:
    # #     print(error)
    print(f"Total Error: {len(sorted_errors)}\n")
    print("Error will be highlight now, and the error will be log in another sheet")
    if len(sorted_errors) == 0:
        return 204, "No error found, can proceed to the next step...."
    else:
        workbook = getWorkbook(workbookID)
        sheet = workbook.get_worksheet_by_id(sheetID)
        clear_formatting.clear_format(workbook, sheetID, list(column_rules.keys()), df, headerIndex)
        error_logging.highlight_error(workbook, sheetID, sorted_errors)
        error_logging.log_error(workbook, sorted_errors, sheet.title)
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


def run_validation(workbookID, sheetID):
    WORKSHEET_DIR = os.path.join(BASE_DIR, "worksheet_column")
    file_name = glob.glob(f'{WORKSHEET_DIR}/*{sheetID}*')

    if not file_name:
        return {"code": 404, "message": "The correspond column rules json file haven't been create, please create and configure it now"}
    else:
        with open(file_name[0], "r") as file:
            column_rules = json.load(file)

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

        correctFormat = formatCheck(records[header_idx], column_rules)
        # correctFormat = False
        if correctFormat:
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
            return {"code": 400, "message": "Add/remove column or change column name is prohibited, please change back to original"}