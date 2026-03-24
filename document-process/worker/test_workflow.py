import boto3
import requests
import json
import time

LOCALSTACK = "http://localhost:4566"
API_URL = "http://localhost:4566/restapis/mdirs8rhmf/local/_user_request_/upload"
BUCKET = "document-upload-bucket"
QUEUE_URL = "http://localhost:4566/000000000000/document-processing-queue"

s3 = boto3.client(
    "s3",
    endpoint_url='http://localhost:4566',
)

sqs = boto3.client(
    "sqs",
    endpoint_url='http://localhost:4566',
    region_name='us-east-1',
    aws_access_key_id='test',
    aws_secret_access_key='test'
)

def check_s3():

    print("Checking S3 bucket...")

    time.sleep(2)

    response = s3.list_objects_v2(Bucket=BUCKET)

    objects = response.get("Contents", [])

    for obj in objects:
        print("File found in S3:", obj["Key"])

    return objects


def check_sqs():

    print("Checking SQS queue...")

    response = sqs.receive_message(
        QueueUrl=QUEUE_URL,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=5
    )

    messages = response.get("Messages", [])

    if not messages:
        print("No messages in queue")
        return None

    message = messages[0]

    body = json.loads(message["Body"])

    print("SQS message received:")
    print(json.dumps(body, indent=2))

    sqs.delete_message(
        QueueUrl=QUEUE_URL,
        ReceiptHandle=message["ReceiptHandle"]
    )

    return body


def download_from_s3(bucket, key):

    print("Downloading file from S3...")

    s3.download_file(bucket, key, "downloaded_test.txt")

    print("Downloaded successfully")


def main():

    objects = check_s3()

    if not objects:
        print("Upload failed")
        return

    event = check_sqs()

    if not event:
        print("No event received")
        return

    # record = event["Records"][0]

    # bucket = record["s3"]["bucket"]["name"]
    # key = record["s3"]["object"]["key"]

    bucket = event["bucket"]
    key = event["key"]

    download_from_s3(bucket, key)

    print("Workflow completed successfully")


if __name__ == "__main__":
    main()