from ast import Expression
import json
import uuid
from webbrowser import get
import boto3
import sys
import os
from datetime import datetime, timezone

# Allows import from 'infra/' wherever the script is called
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from infra.config import AWS_CONFIG, DYNAMODB_TABLE, SES_SENDER
from lambdas.notify_order.email_template import build_email

def get_dynamodb_table():
    dynamodb = boto3.resource("dynamodb", **AWS_CONFIG)
    return dynamodb.Table(DYNAMODB_TABLE)

def update_order_status(order_id: str, status: str):
    """
    Update the status of the order in DynamoDB.

    We use update_item instead of put_item to update
    only the field 'status' — without overwrite other fields.
    """
    table = get_dynamodb_table()
    table.update_item(
        Key = {"order_id": order_id},
        UpdateExpression = "SET #s = :status",
        ExpressionAttributeNames = {"#s": "status"}, # 'status' is keyword
        ExpressionAttributeValues = {":status": status}
    )
    print(f"Order status {order_id} updated to '{status}'")

def send_email(order: dict):
    """
    Send a confirmation E-mail via SES.

    The SES requires:
    - Source:      verified sender
    - Destination: recipient(s)
    - Message:     subject + body (html and/or pure text)
    """
    ses = boto3.client("ses", **AWS_CONFIG)
    email = build_email(order)

    # The client e-amil woudl come from registration  — we emulate it here
    customer_email = order.get("customer_email", "cliente@example.com")

    ses.send_email(
        Source=SES_SENDER,
        Destination={
            "ToAddresses": [customer_email]
        },
        Message={
            "Subject": {
                "Data": email["subject"],
                "Charset": "UTF-8"
            },
            "Body": {
                "Text": {
                    "Data": email["text"],
                    "Charset": "UTF-8"
                },
                "Html": {
                    "Data": email["html"],
                    "Charset": "UTF-8"
                }
            }
        }
    )
    print(f"E-mail sent to: {customer_email}")


def lambda_handler(event, context):
    """
    This Lambda is triggered by SQS.
    The 'event' contains a list of messages - the SQS can
    deliver multiple messages at once (in batch), then we iterate over them.
    """
    for record in event["Records"]:

        # The SQS message body can come in two ways:
        # 1. Directly from SQS → body is the JSON of order
        # 2. Via SNS → body has an extra layer with JSON inside the "Message"
        raw_body = json.loads(record["body"])

        if "Message" in raw_body:
            # Came via SNS — we need to umpack
            order = json.loads(raw_body["Message"])
        else:
            # Came from SQS
            order = raw_body

        order_id = order["order_id"]
        customer_name = order["customer_name"]
        product = order["product"]

        print(f"Processing notification for order: {order_id}")

        # 1. Send E-mail
        try:
            send_email(order)
        except Exception as e:
            print(f"Error while sending e-mail: {str(e)}")
            raise

        # 2. Update status to NOTIFIED in DynamoDB
        try:
            update_order_status(order_id, "NOTIFIED")
        except Exception as e:
            print(f"Erro ao atualizar status: {str(e)}")
            raise  # relança o erro para o SQS retentar a mensagem

        print(f"Notificação processada: {customer_name} — {product}")

    return {"statusCode": 200}
