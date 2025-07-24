def clear_format(workbook, sheetID, headers, df, headerIdx):
    clear_formatting_request = {
            "repeatCell": {
                "range": {
                    "sheetId": sheetID,
                    "startRowIndex": headerIdx + 1,
                    "endRowIndex": len(df) + 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": len(headers),
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {
                            "red": 1.0,
                            "green": 1.0,
                            "blue": 1.0
                        }
                    }
                },
                "fields": "userEnteredFormat(backgroundColor)"
            }
        }
    workbook.batch_update({"requests": clear_formatting_request})