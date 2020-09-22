import boto3
from decimal import Decimal
from datetime import datetime
import pathlib
import json


def get_image_labels(s3_bucket, photo):
    client = boto3.client('rekognition')
    response = client.detect_labels(
        Image={'S3Object': {'Bucket': s3_bucket, 'Name': photo}},
        MaxLabels=10)
    return response


def put_image_details(photo, label, confidence):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('my_table-e3959cf')
    response = table.put_item(
       Item={
            'Id': photo,
            'label': label,
            'confidence': Decimal(confidence),
            'timestamp': datetime.utcnow().isoformat()
        }
    )
    return response


def query_images():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('my_table-e3959cf')
    response = table.scan()
    items = []
    for item in response['Items']:
        d = {'id': item['Id'], 'label': item['label'], 'confidence': float(item['confidence']),
             'timestamp': item['timestamp']}
        items.append(d)
    return json.dumps(items)


def process_image(bucket, image):
    ext = pathlib.Path(image).suffix
    if ext in ['.jpg', '.png']:
        label_response = get_image_labels(bucket, image)
        first_label = label_response['Labels'][0]
        dynamodb_response = put_image_details(image, first_label['Name'], first_label['Confidence'])


if __name__ == "__main__":
    #process_image('s3-website-bucket-a2cf93d', 'cityscape.jpg')
    json_data = query_images()
    print(json_data)

