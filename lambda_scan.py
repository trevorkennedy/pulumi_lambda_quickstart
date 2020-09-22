import os
import boto3
import json


def query_images():
    dynamodb = boto3.resource('dynamodb')
    table_name = os.environ['DYNAMODB_TABLE']
    table = dynamodb.Table(table_name)
    response = table.scan()
    items = []
    for item in response['Items']:
        d = {'id': item['Id'], 'label': item['label'], 'confidence': float(item['confidence']),
             'timestamp': item['timestamp']}
        items.append(d)
    return json.dumps(items)


def handler(event, context):
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": query_images()
    }
