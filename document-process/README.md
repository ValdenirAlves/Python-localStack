# 📦 Serverless Document Processing Pipeline

This project demonstrates a serverless, event-driven architecture for file upload and processing using AWS services, simulated locally with LocalStack.

## 🚀 Overview

The application allows users to upload files through an API. Once uploaded, the system stores the file, records metadata, and triggers asynchronous processing using a message queue.

This project was built as a hands-on learning experience to deepen knowledge in Python and AWS serverless architecture.

---

## 🧱 Architecture

The system is composed of the following components:

- FastAPI service to handle file uploads
- API Gateway to expose the Lambda endpoint
- Lambda function for processing uploads
- S3 bucket for file storage
- DynamoDB table for metadata persistence
- SQS queue for asynchronous event processing
- Terraform for infrastructure as code
- LocalStack for local AWS simulation

### 📊 Flow

Client → FastAPI → API Gateway → Lambda → S3  
                                      ↘  
                                       DynamoDB  
                                      ↘  
                                       SQS  

---

## ⚙️ Tech Stack

- Python
- FastAPI
- AWS (Lambda, API Gateway, S3, SQS, DynamoDB)
- Terraform
- LocalStack
- Docker

---

## 📥 Upload Flow

1. User uploads a file via FastAPI endpoint  
2. File is encoded in Base64 and sent to API Gateway  
3. Lambda function:  
   - Decodes file content  
   - Stores file in S3  
   - Saves metadata in DynamoDB  
   - Sends an event to SQS  

---

## 📂 Project Structure

project-root/  
│  
├── app/  
│   └── file-upload.py  
│  
├── lambda/  
│   └── index.py  
│  
├── infrastructure/  
│   └── terraform/  
│       ├── api_gateway.tf  
│       ├── compute.tf  
│       ├── dynamodb.tf  
│       ├── s3.tf  
│       └── sqs.tf  
│  
└── README.md  

---

## 🧪 Running Locally

### Prerequisites

- Docker  
- LocalStack  
- Terraform  
- Python 3.x  

---

### 1. Start LocalStack

docker run -d -p 4566:4566 localstack/localstack

---

### 2. Deploy infrastructure

cd infrastructure/terraform  
terraform init  
terraform apply  

---

### 3. Run FastAPI

uvicorn file-upload:app --reload  

---

### 4. Test the API

Open:

http://localhost:8000/docs  

Upload a file using the `/upload/` endpoint.

---

## 🔍 Verification

### Check S3

aws --endpoint-url=http://localhost:4566 s3 ls s3://document-upload-bucket  

---

### Check DynamoDB
 
aws --endpoint-url=http://localhost:4566 dynamodb scan --table-name documents
---

### Check SQS

aws --endpoint-url=http://localhost:4566 sqs receive-message --queue-url http://localhost:4566/000000000000/document-processing-queue  

---

## 💡 Key Learnings

- Building serverless applications using AWS services  
- Understanding event-driven architecture  
- Using Terraform for infrastructure provisioning  
- Simulating AWS locally with LocalStack  
- Handling file uploads and Base64 encoding in APIs  
- Debugging distributed systems and service integration  

---

## 🚀 Future Improvements

- Add Lambda worker to process SQS messages  
- Implement file validation and error handling  
- Add authentication (JWT)  
- Deploy to real AWS environment  
- Add monitoring and logging  

---

## 📌 Notes

This project runs entirely locally using LocalStack and does not require an AWS account.

---

## 👨‍💻 Author

Backend Developer with 10+ years of experience, expanding into Python and AWS serverless architecture.