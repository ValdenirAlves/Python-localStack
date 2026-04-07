import boto3
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from infra.config import AWS_CONFIG, DYNAMODB_TABLE, SQS_QUEUE_URL, SNS_TOPIC, SES_SENDER

def create_dynamodb_table():
    dynamodb = boto3.client("dynamodb", **AWS_CONFIG)
    try:
        dynamodb.create_table(
            TableName=DYNAMODB_TABLE,
            AttributeDefinitions=[{"AttributeName": "order_id", "AttributeType": "S"}],
            KeySchema=[{"AttributeName": "order_id", "KeyType": "HASH"}],
            BillingMode="PAY_PER_REQUEST"
        )
        print(f"Table '{DYNAMODB_TABLE}' created!")
    except dynamodb.exceptions.ResourceInUseException:
        print(f"Table '{DYNAMODB_TABLE}' already exists, ignoring...")

def create_sqs_queue():
    sqs = boto3.client("sqs", **AWS_CONFIG)
    queue_name = SQS_QUEUE_URL.split("/")[-1]  # extracts 'order-notifications' from URL
    sqs.create_queue(QueueName=queue_name)
    print(f"Queue '{queue_name}' created!")

def create_sns_topic():
    """
    Creates SNS topic and returns the created ARN
    The SNS works like a radio: the topic is the broadcasting station, and the
    subscribers (SQS, e-mail, Lambda) are the listeners.
    Any message plublished in the topic is delivered to all subscribers.
    """
    sns = boto3.client("sns", **AWS_CONFIG)

    # create_topic is idempotent: if it already exists, return the ARN without error.
    response = sns.create_topic(Name=SNS_TOPIC)
    topic_arn = response["TopicArn"]
    print(f"SNS topic '{SNS_TOPIC}' create!")
    print(f"ARN: {topic_arn}")
    return topic_arn

def subscribe_sqs_to_sns(topic_arn: str):
    """
    Connect the SQS queue to SNS topic.
    After that, any message published in the tópic will be delivered 
    automatically in the queue - with no extra code in the lambda
    """

    sns = boto3.client("sns", **AWS_CONFIG)

    # the ARN of the queue has a different format of the URL
    # URL:  http://localhost:4566/000000000000/order-notifications
    # ARN:  arn:aws:sqs:us-east-1:000000000000:order-notifications 
    queue_name = SQS_QUEUE_URL.split("/")[-1] # extract 'order-notifications' from URL
    queue_arn = f"arn:aws:sqs:us-east-1:000000000000:{queue_name}"

    sns.subscribe(
        TopicArn = topic_arn,
        Protocol = "sqs",       # subscriber type
        Endpoint = queue_arn    # receiver
    )
    print(f"Queue '{queue_name}' subscribed to the SNS topic!")

def verify_ses_email():
    """
    Register the sender email address in SES.
    In the real AWS this sends a confirmation email.
    in The localStack, it's instantaneous.
    """
    ses = boto3.client("ses", **AWS_CONFIG)
    ses.verify_email_identity(EmailAddress=SES_SENDER)
    print(f"E-mail '{SES_SENDER}' verified in the SES!")

def create_rest_api():
    apigw = boto3.client("apigateway", **AWS_CONFIG)

    api = apigw.create_rest_api(name="order-api")
    api_id = api["id"]

    print(f"API criada: {api_id}")
    # Ex: api_id = "abc123de"

if __name__ == "__main__":
    print("Creating infrastructure in the LocalStack...")
    create_dynamodb_table()
    create_sqs_queue()
    topic_arn = create_sns_topic()
    subscribe_sqs_to_sns(topic_arn)
    verify_ses_email()
    print("\nInfrastructure done!")