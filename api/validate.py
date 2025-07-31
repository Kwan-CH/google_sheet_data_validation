from fastapi import FastAPI, Query, Body

app = FastAPI()

@app.get("/validate")
async def validate_get(sheetId: str = Query(...), sheetName: list[str] = Query(...)):
    print(f"GET Received sheetId: {sheetId}")
    print(f"GET Received sheetName: {sheetName}")
    return {"status": "success", "sheetId": sheetId, "sheetName": sheetName}

@app.post("/validate")
async def validate_post(payload: dict = Body(...)):
    print(f"POST Received payload: {payload}")
    return {"status": "success", "payload": payload}
