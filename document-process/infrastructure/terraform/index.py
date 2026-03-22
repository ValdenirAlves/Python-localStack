import json
import boto3
import base64

BUCKET = 'document-upload-bucket'
TABLE = 'documents'
QUEUE = "http://localhost:4566/000000000000/document-processing-queue"

# clientes apontando para LocalStack
# Usa localhost.localstack.cloud que é resolvido dentro da Lambda no LocalStack
s3 = boto3.client("s3", endpoint_url="http://localhost.localstack.cloud:4566")
dynamodb = boto3.client("dynamodb", endpoint_url="http://localhost.localstack.cloud:4566")
sqs = boto3.client("sqs", endpoint_url="http://localhost.localstack.cloud:4566")

def handler(event, context):

    print("EVENT:", event)

    # recebe JSON com filename + content
    # body = json.loads(event.get("body", "{}"))
    body = json.loads(event["body"])
    file_name = body.get("filename")
    content = base64.b64decode(body["content"])

    if not file_name or not content:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "File name and content are required!"})
        }
    
    

    # grava no S3
    s3.put_object(Bucket=BUCKET, Key=file_name, Body=content)

    # grava metadados no DynamoDB
    dynamodb.put_item(
        TableName=TABLE,
        Item={
            "document_id": {"S": file_name},
            "size": {"N": str(len(content))}
        }
    )

    # envia evento para SQS
    sqs.send_message(
        QueueUrl=QUEUE,
        MessageBody=json.dumps({
            "bucket": BUCKET,
            "key": file_name
        })
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "bucket": BUCKET,
            "key": file_name
        })
    }