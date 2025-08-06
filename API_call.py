from fastapi import FastAPI, Query, Body, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from core import main
from core.config import read_column
import os

app = FastAPI()

# @app.get("/validate")
# async def validate_get(sheetId: str = Query(...), sheetName: list[str] = Query(...)):
#     print(f"GET Received sheetId: {sheetId}")
#     print(f"GET Received sheetName: {sheetName}")
#     return {"status": "success", "sheetId": sheetId, "sheetName": sheetName}

JSON_FILE_PATH = "./worksheet_column"
os.makedirs(JSON_FILE_PATH, exist_ok=True)

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

@app.get("/return-json")
async def return_json_file():
    try:
        json_files = [f for f in os.listdir(JSON_FILE_PATH) if f.endswith(".json")]
        return {"files": json_files}
    except Exception as e:
        return {"error": str(e)}

@app.get("/download-json")
async def download_json_file(filename: str = Query(...)):
    file_path = os.path.join(JSON_FILE_PATH, filename)
    if not filename.endswith(".json") or not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found.")
    
    return FileResponse(
        path=file_path,
        media_type="application/json",
        filename=filename
    )

@app.post("/upload-json")
async def upload_json_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Only .json files are allowed")

    file_path = os.path.join(JSON_FILE_PATH, file.filename)

    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

    return {"message": "File uploaded successfully", "filename": file.filename}