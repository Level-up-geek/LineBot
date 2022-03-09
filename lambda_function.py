import json
from dotenv import dotenv_values

def lambda_handler(event, context):
    # TODO implement
    config = dotenv_values(".env")
    return {
        'statusCode': 200,
        'body': json.dumps(config)
    }