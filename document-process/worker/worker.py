import boto3
import json
import time
import os

ENDPOINT    = 'http://localhost:4566'
QUEUE_URL   = "http://localhost:4566/000000000000/document-processing-queue"
REGION      = 'us-east-1'

# Define a local directory to download files in
DOWNLOAD_DIR = './downloads'
os.makedirs(DOWNLOAD_DIR, exist_ok=True) # create the folder

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

         # Ignore test message form S3
        if body.get("Event") == "s3:TestEvent":
            sqs.delete_message(
                QueueUrl=QUEUE_URL,
                ReceiptHandle=message['ReceiptHandle']
            )
            print("S3 test event ignored.")
            continue

        try:
            for record in body.get('Records', []):
                bucket    = record["s3"]["bucket"]["name"]
                file_name = record["s3"]["object"]["key"]

                print(f'Message received: {file_name}')

                local_path = os.path.join(DOWNLOAD_DIR, file_name)
                s3.download_file(bucket, file_name, local_path)
                print(f'File downloaded: {file_name} -> {local_path}')

            sqs.delete_message(
                QueueUrl=QUEUE_URL,
                ReceiptHandle=message['ReceiptHandle']
            )
            print('Message removed from queue!')
        except Exception as error:
            print(f'Error processing {file_name}: {str(error)}')

    time.sleep(2)