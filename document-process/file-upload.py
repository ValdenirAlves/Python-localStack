from fastapi import FastAPI, UploadFile, File
import requests
import base64

app = FastAPI()

# URL API Gateway LocalStack
API_URL = "http://localhost:4566/restapis/gggiigxn4v/local/_user_request_/upload"

@app.post("/upload/")
async def upload(file: UploadFile = File(...)):
    content = await file.read()
    payload = {
        "filename": file.filename,
        "content": base64.b64encode(content).decode()  # envia base64
    }
    resp = requests.post(API_URL, json=payload)
    return resp.json()
