from functools import partial
from inspect import signature

import pandas as pd

import json
from components import clear_formatting, error_logging
from components.customError import unrecognizedRule
from components.getWorkbook import getWorkbook
from components.sort_location import sort_error_list
from components.validator import Validator

with open("json/config.json", "r") as file:
    config = json.load(file)

with open("json/checkMap.json", "r") as file:
    rule_map = json.load(file)

name = "test_data"
# name = input("Please enter the json file to be used\nName: ").strip()
with open(f"worksheet_column/{name}.json", "r") as file:
    column_rules = json.load(file)

# with open(f"worksheet_column/column_rules.json", "r") as file:
#     column_rules = json.load(file)

def highlightError(df, sorted_errors):
    print("All data has been validated, below are the errors found")
    # for error in sorted_errors:
    #     print(error)
    print(f"Total Error: {len(sorted_errors)}\n")

    print("Error will be highlight now, and the error will be log in another sheet")

    workbook = getWorkbook()

    clear_formatting.clear_format(workbook, config["sheetID"], list(column_rules.keys()), df, config["headerIndex"])
    error_logging.highlight_error(workbook, config["sheetID"], sorted_errors)
    error_logging.log_error(workbook, sorted_errors)

def main():
    workbook = getWorkbook()
    sheet = workbook.worksheet(config["worksheetName"])
    records = sheet.get_all_values()
    data = records[config["headerIndex"] + 1:]

    df = pd.DataFrame(data, columns=column_rules.keys())
    checker = Validator(df)

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

    highlightError(df, sorted_errors)

main()