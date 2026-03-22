# worker manual

import boto3
import time

endpoint_url = 'http://localhost:4566'
queue_url = "http://localhost:4566/000000000000/minha-fila-teste"
bucket_name = "meu-bucket-teste"
region_name = 'us-eat-1'

# conn localStack
sqs = boto3.client(
    "sqs",
    endpoint_url = endpoint_url,
    region_name = region_name,
    aws_access_key_id = 'test',
    aws_secret_access_key = 'test'
    )

s3 = boto3.client(
    "s3",
    endpoint_url = endpoint_url,
    region_name = region_name,
    aws_access_key_id = 'test',
    aws_secret_access_key = 'test'
)

print('Worker started. Listening to queue...')

while True:
    response = sqs.receive_message(
        QueueUrl = queue_url,
        MaxNumberOfMessages = 1,
        WaitTimeSeconds = 5
    )

    messages = response.get('Messages', [])

    for message in messages:
        file_name = message["Body"]

        print('Message received:', file_name)

        # Download S3 file
        s3.download_file(bucket_name, file_name, f'download_{file_name}')

        print('File downloaded:', file_name)

        # delete message from the queue
        sqs.delete_message(
            QueueUrl = queue_url,
            ReceiptHandle = message['ReceiptHandle']
        )

        print('Message removed from queue!')

    time.sleep(2)