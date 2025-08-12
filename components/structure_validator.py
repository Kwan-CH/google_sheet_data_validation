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

# Helper function to get the column label based on the column number
def number_to_excel_column(n):
    """
    Convert a number to its Excel column label.
    """
    if n < 1:
        raise ValueError("Column number must be positive integer.")
    
    column_label = ""

    while n > 0:
        n -= 1
        rem = n % 26
        column_label += chr(rem + ord('A'))
        n //= 26

    # reverse the string
    return column_label[::-1]

# Check if the sheet header row is in the exact order and name as specificed in ./worksheet_column/[Title].json
def correctColumnHeaderOrder(headers, headers_order):
    out_of_order = []

    max_len = max(len(headers_order), len(headers))
    
    for i in range(max_len):
        exp = headers_order[i] if i < len(headers_order) else None
        act = headers[i] if i < len(headers) else None

        if exp != act:
            out_of_order.append(f"Expected: {exp}, Found: {act} at column {number_to_excel_column(i + 1)}")

    # Return status (T/F) and show columns with error
    if not out_of_order:
        return {"status": True, "error": ""}
    else:
        return {"status": False, "error": "Please do not change the order of column headers", "detail": out_of_order}

def correctFormat(sheet, headers, column_rules, headers_order):
    column_name = correctColumnName(headers, column_rules)
    column_number = correctColumnNumber(headers, column_rules)
    sheet_name = correctSheetName(sheet)
    header_order = correctColumnHeaderOrder(headers, headers_order)

    message = "There are some structure error as following:\n"
    if not column_name.get("status"):
        message += f"-{column_name.get('error')}\n"

    if not column_number.get("status"):
        message += f"-{column_number.get('error')}\n"

    if not sheet_name.get("status"):
        message += f"-{sheet_name.get('error')}\n"

    if not header_order.get("status"):
        message += f"-{header_order.get('error')}\n"
        for msg in header_order.get("detail"):
            message += f"-{msg}\n"

    status = column_name.get("status") and column_number.get("status") and sheet_name.get("status") and header_order.get("status")
    # message += "Kindly revert your changes that stated"

    return {"status": status, "message": message}