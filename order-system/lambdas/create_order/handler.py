import json
import uuid
import boto3
import sys
import os
from datetime import datetime, timezone

# Allows import from 'infra/' wherever the script is called
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from infra.config import AWS_CONFIG, DYNAMODB_TABLE, SQS_QUEUE_URL

def get_dynamodb_table():
    """
    Creates and returns a reference to DynamoDB table.
    
    We separated them according to their function for two reasons:
    1. Facilitates the replacement by environment variables in the future
    2. Facilitates to write tests (you can replace this function by a mock)
    """
    dynamodb = boto3.resource("dynamodb", **AWS_CONFIG)
    return dynamodb.Table(DYNAMODB_TABLE)

def get_sqs_client():
    """
    Returns a client SQS.
    Note: SQS uses 'client', not 'resource' as DynamoDB.
    Difference: client returns dict, resource returns Python object.
    For SQS, client is more used.
    """
    return boto3.client("sqs", **AWS_CONFIG)

def send_to_queue(order: dict):
    sqs = get_sqs_client()
    sqs.send_message(
        QueueUrl=SQS_QUEUE_URL,
        MessageBody=json.dumps(order)
    )

    print(f'Order sent to queue: {order["order_id"]}')

def lambda_handler(event, context):
    # 1. Extract the body from the request and validate it.
    # The API Gateway sends the body as string, so we need convert it to dict
    body = json.loads(event.get("body", "{}"))

    # Validate required fields
    required_fields = ["customer_name", "product", "quantity"]
    missing_fields = []
    for field in required_fields:
        if field not in body:
            missing_fields.append(field)

    if missing_fields:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "error": "Missing required fields:",
                "missing_fields": missing_fields
            })
        }

    # # 2. Create the object order
    order = {
        "order_id": str(uuid.uuid4()),
        "customer_name": body["customer_name"],
        "product": body["product"],
        "quantity": int(body["quantity"]),
        "status": "RECEIVED",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    # 3. Save into DynamoDB
    try:
        table = get_dynamodb_table()
        table.put_item(Item=order)
        print(f"Order saved in DynamoDB: {order['order_id']}")
    except Exception as e:
        print(f"Erro while saving in DynamoDB: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal error while saving order"})
        }

    # 4. Queue the event in SQS
    try:
        send_to_queue(order)
    except Exception as e:
        # Order was saved already - no error 500 returned to client
        # Only log - the process can be done later
        print(f'Alert: failed while sending order to queue! Order was saved, but notification is pending: {str(e)}')

    # 5. Return sucess
    return {
        "statusCode": 201,
        "body": json.dumps({
            "message": "Order received with success!",
            "order_id": order["order_id"]
        })
    }