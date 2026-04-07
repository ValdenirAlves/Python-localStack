from lambdas.create_order.handler import lambda_handler as create_order
from lambdas.notify_order.handler import lambda_handler as notify_order

# 1. Cria o pedido
print("=== Criando pedido ===")
response = create_order(
    {"body": '{"customer_name": "João Silva", "product": "Notebook", "quantity": 1}'},
    None
)
print("Resposta:", response)

# 2. Trigger the Lambda Notificador
import json
body = json.loads(response["body"])
order_id = body["order_id"]

print("\n=== Notificando pedido ===")
fake_sqs_event = {
    "Records": [{
        "body": json.dumps({
            "order_id": order_id,
            "customer_name": "João Silva",
            "product": "Notebook",
            "quantity": 1,
            "status": "RECEIVED",
            "created_at": "2024-01-01T00:00:00"
        })
    }]
}
notify_order(fake_sqs_event, None)

# 3. Confirm hecks the status in DynamoDB
import boto3, sys, os
sys.path.append(".")
from infra.config import AWS_CONFIG, DYNAMODB_TABLE
table = boto3.resource("dynamodb", **AWS_CONFIG).Table(DYNAMODB_TABLE)
item = table.get_item(Key={"order_id": order_id})["Item"]
print(f"\nFinal status in DynamoDB: {item['status']}")

# 4. Confirm e-mails sent in the LocalStack
ses = boto3.client("ses", **AWS_CONFIG)
stats = ses.get_send_statistics()
print(f"Total of e-mail sent: {len(stats['SendDataPoints'])}")




# Simulating what would be sent by API Gateway
# fake_event = {
#     'body': '{"customer_name": "Valdenir Alves", "product": "Laptop", "quantity": 1}'
# }

# response = lambda_handler(fake_event, None)
# print("Lambda response:", response)