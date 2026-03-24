# worker.py
# Agora o Worker processa arquivos automaticamente quando eles chegam no S3.

import boto3
import time
import json

sqs = boto3.client('sqs', endpoint_url="http://localhost:4566")
s3 = boto3.client('s3', endpoint_url="http://localhost:4566")

queue_url = "http://localhost:4566/000000000000/document-processing-queue"
bucket_name = "document-upload-bucket"
region_name = 'us-eat-1'

while True:
    resp = sqs.receive_message(
        QueueUrl=queue_url, 
        MaxNumberOfMessages=1,
        WaitTimeSeconds=20 
    )
    messages = resp.get('Messages', [])
    if messages:
        for msg in messages:
            file_name = msg["Body"]

            print(f"Message received: {file_name}")

            # Baixar o arquivo do S3
            s3.download_file(bucket_name, file_name, f'download_{file_name}')

            # Apagar a mensagem da fila
            sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=msg['ReceiptHandle'])
    # time.sleep(1)