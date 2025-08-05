import json
import os
import glob

from components.getWorkbook import getWorkbook

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CONFIG_JSON_PATH = os.path.join(BASE_DIR, 'json', 'config.json')
WORKSHEET_COLUMN_PATH = os.path.join(BASE_DIR, 'worksheet_column')

def write_column_rule(sheet, headers):
    name = f"{sheet.title}-column_rules"
    headers_json = {
        header: {
            "rule": "",
            "param":{
                "allowEmpty": False
            }
        }
        for header in headers
    }
    with open(os.path.join(WORKSHEET_COLUMN_PATH, f"{name}.json"), "x") as file:
        json.dump(headers_json, file, indent=4)

def read_column(workbookID, sheetID):
    workbook = getWorkbook(workbookID)
    sheet = workbook.get_worksheet_by_id(sheetID)

    header_idx = 0
    records = sheet.get_all_values()
    for record in records:
        if "#" in record[0]:
            pass
        else:
            header_idx = records.index(record)
            break
    headers = records[header_idx]

    WORKSHEET_DIR = os.path.join(BASE_DIR, "worksheet_column")
    file_name = glob.glob(f'{WORKSHEET_DIR}/*{sheetID}*')

    if file_name:
        return {"code": 409, "message": f"A file with the same configuration format existed, please look for file with the code and the gid at the url: {sheetID}"}
    else:
        write_column_rule(sheet, headers)
        return {"code": 201, "message": "The column rule file is created, you can now configure the rules"}