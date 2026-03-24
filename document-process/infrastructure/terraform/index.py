from datetime import datetime, timezone
import json
import uuid
import boto3
import base64
import traceback

BUCKET = 'document-upload-bucket'
TABLE = 'documents'
QUEUE_URL = "http://localhost.localstack.cloud:4566/000000000000/document-processing-queue"

ENDPOINT = "http://localhost.localstack.cloud:4566"

s3       = boto3.client("s3",         endpoint_url=ENDPOINT, region_name="us-east-1", aws_access_key_id="test", aws_secret_access_key="test")
dynamodb = boto3.resource("dynamodb", endpoint_url=ENDPOINT, region_name="us-east-1", aws_access_key_id="test", aws_secret_access_key="test")
sqs      = boto3.resource("sqs",      endpoint_url=ENDPOINT, region_name="us-east-1", aws_access_key_id="test", aws_secret_access_key="test")

def handler(event, context):
    print("EVENT:", event)

    body = json.loads(event["body"])
    file_name = body.get("filename")
    content_b64 = body.get("content")

    if not file_name or not content_b64:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "File name and content are required!"})
        }

    content = base64.b64decode(content_b64)

    # Grava no S3
    s3.put_object(Bucket=BUCKET, Key=file_name, Body=content)

    # Grava metadados no DynamoDB
    try:
        table = dynamodb.Table(TABLE)
        table.put_item(
            Item={
                "document_id": str(uuid.uuid4()),
                "file_name": file_name,
                "bucket": BUCKET,
                "uploaded_at": datetime.now(timezone.utc).isoformat(),
                "size": len(content)
            }
        )
    except Exception as e:
        print("ERROR:", str(e))
        print(traceback.format_exc())
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

    # Envia evento para SQS
    queue = sqs.Queue(QUEUE_URL)
    queue.send_message(
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