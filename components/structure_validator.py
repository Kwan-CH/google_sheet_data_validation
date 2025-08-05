#sheet title check using jsn file name, column number use len(), column name use in
import glob
import os

def correctColumnName(headers, column_rules):
    for header in headers:
        if header.strip() in column_rules.keys():
            pass
        else:
            return {"status": False, "error": "Please do not change the column headers' name"}
    return {"status": True, "error": ""}

def correctColumnNumber(headers, column_rules):
    if len(headers) == len(column_rules.keys()):
        return {"status": True, "error": ""}
    else:
        return {"status": False, "error": "Please do not add/remove any column"}

def correctSheetName(sheet):
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    WORKSHEET_DIR = os.path.join(BASE_DIR, "worksheet_column")
    file_name = glob.glob(f'{WORKSHEET_DIR}/*{sheet.title}*')
    if file_name:
        return {"status": True, "error": ""}
    else:
        return {"status": False, "error": "Please do not change the sheet's name"}

def correctFormat(sheet, headers, column_rules):
    column_name = correctColumnName(headers, column_rules)
    column_number = correctColumnNumber(headers, column_rules)
    sheet_name = correctSheetName(sheet)

    message = "There are some structure error as following:\n"
    if not column_name.get("status"):
        message += f"-{column_name.get('error')}\n"

    if not column_number.get("status"):
        message += f"-{column_number.get('error')}\n"

    if not sheet_name.get("status"):
        message += f"-{sheet_name.get('error')}\n"

    status = column_name.get("status") and column_number.get("status") and sheet_name.get("status")
    # message += "Kindly revert your changes that stated"

    return {"status": status, "message": message}