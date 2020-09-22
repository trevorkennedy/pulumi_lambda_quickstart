import boto3
import json
import uuid
from decimal import Decimal
from urllib.parse import unquote_plus
import os
from datetime import datetime
import pathlib


# Call Rekognition API with an image from the S3 bucket
def get_image_labels(s3_bucket, photo):
    client = boto3.client('rekognition')
    response = client.detect_labels(
        Image={'S3Object': {'Bucket': s3_bucket, 'Name': photo}},
        MaxLabels=10)
    return response


# Save image name, labels and timestamp to the DynamoDB table
def put_image_details(photo, label, confidence):
    dynamodb = boto3.resource('dynamodb')
    dynamodb_table = os.environ['DYNAMODB_TABLE']
    table = dynamodb.Table(dynamodb_table)
    response = table.put_item(
       Item={
            'Id': photo,
            'label': label,
            'confidence': Decimal(confidence),
            'timestamp': datetime.utcnow().isoformat()
        }
    )
    return response


# Get the first label of an image and persist it to DynamoDB
def process_image(bucket, image):
    ext = pathlib.Path(image).suffix
    if ext in ['.jpg', '.png']:
        label_response = get_image_labels(bucket, image)
        first_label = label_response['Labels'][0]
        dynamodb_response = put_image_details(image, first_label['Name'], first_label['Confidence'])


# Process each new file added to the S3 bucket
def lambda_handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])
        process_image(bucket, key)
    return True
