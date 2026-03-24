import boto3
import json
import time

ENDPOINT    = 'http://localhost:4566'
QUEUE_URL   = "http://localhost:4566/000000000000/document-processing-queue"
REGION      = 'us-east-1'

sqs = boto3.client("sqs", endpoint_url=ENDPOINT, region_name=REGION, aws_access_key_id='test', aws_secret_access_key='test')
s3  = boto3.client("s3",  endpoint_url=ENDPOINT, region_name=REGION, aws_access_key_id='test', aws_secret_access_key='test')

print('Worker started. Listening to queue...')

while True:
    response = sqs.receive_message(
        QueueUrl=QUEUE_URL,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=5
    )

    for message in response.get('Messages', []):
        body      = json.loads(message["Body"])
        bucket    = body["bucket"]
        file_name = body["key"]

        print(f'Message received: {file_name}')

        s3.download_file(bucket, file_name, f'/tmp/download_{file_name}')
        print(f'File downloaded: {file_name}')

        sqs.delete_message(
            QueueUrl=QUEUE_URL,
            ReceiptHandle=message['ReceiptHandle']
        )
        print('Message removed from queue!')

    time.sleep(2)