from fastapi import FastAPI, Query, Body
from core import main
from core.config import read_column

app = FastAPI()

# @app.get("/validate")
# async def validate_get(sheetId: str = Query(...), sheetName: list[str] = Query(...)):
#     print(f"GET Received sheetId: {sheetId}")
#     print(f"GET Received sheetName: {sheetName}")
#     return {"status": "success", "sheetId": sheetId, "sheetName": sheetName}

@app.post("/validate")
async def validate_post(payload: dict = Body(...)):
    worksheets = payload.get("worksheets")
    for item in worksheets:
        workbookID = item.get('workbookID')
        sheetID = item.get('sheetID')
        sheetName = item.get('sheetName')
        print(sheetName)
        response= main.run_validation(workbookID, sheetID, sheetName)
        print(response.get("message"))
        return {"code": response.get("code"), "message": f"{response.get("message")}"}

@app.post("/initialize")
async def initialize_post(payload: dict = Body(...)):
    worksheets = payload.get("worksheets")
    for worksheet in worksheets:
        response = read_column(worksheet.get("workbookID"), worksheet.get("sheetID"))
        return {"code": response.get("code"), "message": f"{response.get("message")}"}

