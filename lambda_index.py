import json

def handler(event, context):
    """
    Função Lambda de exemplo
    """
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Hello from Lambda!',
            'event': event
        })
    }
