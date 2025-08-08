from fastapi import FastAPI, Query, Body, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from core import validation
from core.config import check_json_rule_existence
from typing import List
import os
import glob
import shutil

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

        response= validation.run_validation(workbookID, sheetID, sheetName)
        return {"code": response.get("code"), "message": f"{response.get("message")}"}

@app.post("/initialize")
async def initialize_post(payload: dict = Body(...)):
    worksheets = payload.get("worksheets")
    for worksheet in worksheets:
        response = check_json_rule_existence(worksheet.get("workbookID"), worksheet.get("sheetID"))
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
    file_path = glob.glob(f'{JSON_FILE_PATH}/*{filename}*')

    if not file_path:
        raise HTTPException(status_code=404, detail="File not found.")
    
    return FileResponse(
        path=file_path[0],
        media_type="application/json",
        filename=filename
    )

@app.post("/upload-json")
async def upload_json_files(files: List[UploadFile] = File(...)):
    saved_files = []
    for file in files:
        if not file.filename.endswith(".json"):
            raise HTTPException(status_code=400, detail=f"{file.filename} is not a JSON file.")
        
        save_path = os.path.join(JSON_FILE_PATH, file.filename)
        try:
            with open(save_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")
        finally:
            file.file.close()

        saved_files.append(file.filename)
    
    return {"uploaded_files": saved_files}