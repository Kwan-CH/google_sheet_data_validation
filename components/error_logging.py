import gspread
from gspread.utils import a1_to_rowcol


def highlight_error(workbook, sheetID, sorted_errors):
    requests = []
    for error in sorted_errors:
        locations = error.get("location")
        if not locations:
            continue

        # support multiple A1 locations separated by comma
        for cell in locations.split(","):
            cell = cell.strip()  # remove spaces

            row_location, col_location = a1_to_rowcol(cell)

            requests.append({
                "repeatCell": {
                    "range": {
                        "sheetId": sheetID,
                        "startRowIndex": row_location - 1,
                        "endRowIndex": row_location,
                        "startColumnIndex": col_location - 1,
                        "endColumnIndex": col_location,
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": {
                                "red": 1.0,
                                "green": 0.0,
                                "blue": 0.0
                            }
                        }
                    },
                    "fields": "userEnteredFormat(backgroundColor)"
                }
            })

    workbook.batch_update({"requests": requests})


def log_error(workbook, sheetTitle, sorted_errors=None):
    if isinstance(sorted_errors, str):
        rows = [[sorted_errors]]
    else:
        rows = [['Location', 'Error']]
        rows += [[entry['location'], entry['error']] for entry in sorted_errors]

    try:
        error_ws = workbook.worksheet(f'{sheetTitle}-Error Log')
    except gspread.WorksheetNotFound:
        error_ws = workbook.add_worksheet(title=f'{sheetTitle}-Error Log', rows=len(rows), cols=len(rows[0]))

    error_ws.clear()
    error_ws.update(range_name='A1', values=rows)

    body = {
        "requests": [
            {
                "autoResizeDimensions": {
                    "dimensions": {
                        "sheetId": error_ws.id,
                        "dimension": "COLUMNS",
                        "startIndex": 0,
                        "endIndex": len(rows[0])
                    }
                }
            }
        ]
    }
    workbook.batch_update(body)
