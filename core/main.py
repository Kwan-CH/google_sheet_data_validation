from functools import partial

import pandas as pd

import json
from components import clear_formatting, error_logging
from components.customError import unrecognizedRule
from components.getWorkbook import getWorkbook
from components.sort_location import sort_error_list
from components.validator import Validator

with open("../json/config.json", "r") as file:
    config = json.load(file)

with open("../json/checkMap.json", "r") as file:
    rule_map = json.load(file)
name = "sample"
# name = input("Please enter the json file to be used\nName: ").strip()
with open(f"worksheet_column/{name}.json", "r") as file:
    column_rules = json.load(file)

# with open(f"worksheet_column/column_rules.json", "r") as file:
#     column_rules = json.load(file)

def highlightError(workbookID, sheetID, df, sorted_errors, headerIndex):
    print("All data has been validated, below are the errors found")
    # for error in sorted_errors:
    #     print(error)
    print(f"Total Error: {len(sorted_errors)}\n")

    print("Error will be highlight now, and the error will be log in another sheet")

    if len(sorted_errors) == 0:
        print("No error found, can proceed to the next step....")
    else:
        workbook = getWorkbook(workbookID)
        clear_formatting.clear_format(workbook, sheetID, list(column_rules.keys()), df, headerIndex)
        error_logging.highlight_error(workbook, sheetID, sorted_errors)
        error_logging.log_error(workbook, sorted_errors)

def formatCheck(headers):
    correctFormat = True
    for header in headers:
        if header.strip() in column_rules.keys():
            pass
        else:
            correctFormat = False
            break
    return correctFormat


def main(workbookID, sheetID):
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

    correctFormat = formatCheck(records[header_idx])
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
        highlightError(workbookID, sheetID, df, sorted_errors, header_idx)
    else:
        return "Changing file/sheet name or add/delete column is strictly prohibited, please revert those changes"

# main("1hcl6MOoWldcINFElTElvEuJoG0HU3OpmZMCf8UOQHYo", "1122075977")