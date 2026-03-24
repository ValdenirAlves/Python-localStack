# file-upload.py
# FastAPI para upload de arquivos para o S3 via API Gateway LocalStack
# pip install fastapi uvicorn requests
# rodar: uvicorn file-upload:app --reload na pasta do arquivo
# testar: curl -X POST -F "file=@teste.txt" http://localhost:8000/upload/
# ou http://localhost:8000/docs
# verificar se o arquivo foi uploadado no S3: aws s3 ls s3://document-upload-bucket
# verificar se o arquivo foi processado no Lambda: aws lambda list-functions
# verificar se o arquivo foi processado no DynamoDB: aws dynamodb scan --table-name documents
# verificar se o arquivo foi processado na fila: aws sqs receive-message --queue-url http://localhost:4566/000000000000/document-processing-queue


from fastapi import FastAPI, UploadFile, File
import requests
import base64

app = FastAPI()

# URL API Gateway LocalStack
API_URL = "http://localhost:4566/restapis/4peooll1hk/local/_user_request_/upload"

@app.post("/upload/")
async def upload(file: UploadFile = File(...)):
    content = await file.read()
    payload = {
        "filename": file.filename,
        "content": base64.b64encode(content).decode()  # envia base64
    }
    resp = requests.post(API_URL, json=payload)
    return resp.json()
