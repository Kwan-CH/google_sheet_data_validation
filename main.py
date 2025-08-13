from pathlib import Path

from fastapi import FastAPI, Query, Body, HTTPException, UploadFile, File, Request
from fastapi.responses import FileResponse, JSONResponse

from components.custom_error import *
from core import validation
from core.config import check_json_rule_existence
from typing import List
import os
import shutil

app = FastAPI()

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Google Sheet API Service 🚀",
        "endpoints": [
            "/validate",
            "/initialize",
            "/return-json",
            "/download-json",
            "/upload-json"
        ]
    }

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
        raise HTTPException(status_code=response.get("code"), detail=f"{response.get("message")}")

@app.post("/initialize")
async def initialize_post(payload: dict = Body(...)):
    worksheets = payload.get("worksheets")
    for worksheet in worksheets:
        response = check_json_rule_existence(worksheet.get("workbookID"), worksheet.get("sheetID"))
        raise HTTPException(status_code=response.get("code"), detail=f"{response.get("message")}")

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
    try:
        with open(file_path, "r") as file:
            return FileResponse(
                path=Path(file_path),
                media_type="application/json",
                filename=filename
            )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found.")

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

@app.delete("/delete-json")
async def delete_json_file(filename: str = Query(..., description="Name of the file"),):

    file_path = os.path.join(JSON_FILE_PATH, filename)

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found.")

    try:
        os.remove(file_path)
        return {"message": f"{filename} deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

@app.exception_handler(Exception)
async def custom_exception_handler(request: Request, exc: Exception):
    # Only catch your defined exceptions
    if isinstance(exc, (
        missingConfigJSON, missingField, unrecognizedRule,
        invalidMinMax, invalidArgs, missingPair
    )):
        return JSONResponse(
            status_code=400,
            content={"error": str(exc)}
        )
    # Otherwise, let FastAPI handle it normally
    raise exc