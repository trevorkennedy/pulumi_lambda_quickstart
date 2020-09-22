import mimetypes
import os
import pulumi
import iam
from pulumi import export, FileAsset, ResourceOptions
from pulumi_aws import s3, lambda_, apigateway
from components import StaticWebSite, dynamodb_table


# S3
website = StaticWebSite('s3-website', 'www', 'index.html', '404.html')
web_bucket = website.s3_bucket

# DynamoDB
db = dynamodb_table("my_table")

# Lambda function and API Gateway
LAMBDA_SCAN_SOURCE = 'lambda_scan.py'
LAMBDA_SCAN_PACKAGE = 'lambda_scan.zip'
LAMBDA_VERSION = '1.0.0'
os.system('zip %s %s' % (LAMBDA_SCAN_PACKAGE, LAMBDA_SCAN_SOURCE))

mime_type, _ = mimetypes.guess_type(LAMBDA_SCAN_PACKAGE)
obj = s3.BucketObject(
            LAMBDA_VERSION+'/'+LAMBDA_SCAN_PACKAGE,
            bucket=web_bucket.id,
            source=FileAsset(LAMBDA_SCAN_PACKAGE),
            content_type=mime_type
            )

scan_fn = lambda_.Function(
    'DynamoImagesScan',
    s3_bucket=web_bucket.id,
    s3_key=LAMBDA_VERSION+'/'+LAMBDA_SCAN_PACKAGE,
    handler="lambda_scan.handler",
    runtime="python3.7",
    role=iam.lambda_role.arn,
    environment={"variables": {"DYNAMODB_TABLE": db.id}}
)

scan_api = apigateway.RestApi(
    str(scan_fn.id),
    description='Pulumi Lambda API Gateway Example'
)

proxy_root_met = apigateway.Method(
    'proxy_root',
    rest_api=scan_api,
    resource_id=scan_api.root_resource_id,
    http_method='ANY',
    authorization='NONE'
)

scan_root_int = apigateway.Integration(
    'lambda_root',
    rest_api=scan_api,
    resource_id=proxy_root_met.resource_id,
    http_method=proxy_root_met.http_method,
    integration_http_method='POST',
    type='AWS_PROXY',
    uri=scan_fn.invoke_arn
)

scan_dep = apigateway.Deployment(
    'images_scan',
    rest_api=scan_api,
    stage_name="images_scan-dev",
    __opts__=ResourceOptions(depends_on=[scan_root_int])
)

scan_perm = lambda_.Permission(
    "apigw",
    statement_id="AllowAPIGatewayInvoke",
    action="lambda:InvokeFunction",
    function=scan_fn,
    principal="apigateway.amazonaws.com",
    source_arn=scan_dep.execution_arn.apply(lambda x: f"{x}/*/*")
)

# Lambda function for S3 trigger
lambda_rekognition = lambda_.Function(
    resource_name='ImagesRekognition',
    role=iam.lambda_role.arn,
    runtime="python3.7",
    handler="lambda_rekognition.lambda_handler",
    code=pulumi.AssetArchive({
        '.': pulumi.FileArchive('./lambda_rekognition')
    }),
    environment={"variables": {"DYNAMODB_TABLE": db.id}}
)

# Give bucket permission to invoke Lambda
lambda_event = lambda_.Permission(
    resource_name="lambda_img_event",
    action="lambda:InvokeFunction",
    principal="s3.amazonaws.com",
    source_arn=web_bucket.arn,
    function=lambda_rekognition.arn
)

# Bucket notification that triggers Lambda on Put operation - For JPG
bucket_notification = s3.BucketNotification(
    resource_name="s3_notification",
    bucket=web_bucket.id,
    lambda_functions=[
        {
            "lambda_function_arn": lambda_rekognition.arn,
            "events": ["s3:ObjectCreated:*"],
            "filterSuffix":".jpg"
        },
        {
            "lambda_function_arn": lambda_rekognition.arn,
            "events": ["s3:ObjectCreated:*"],
            "filterSuffix":".png"
        }
    ]
)

# Export the name of the bucket
# List bucket with:
# aws s3 ls $(pulumi stack output bucket_name)
export('bucket_name', web_bucket.id)
# Export the website url
export('website_url', web_bucket.website_endpoint)
# Export the DynamoDB table name
export('table_name',  db.id)
# Export the name of the lambda
# Test with:
# aws lambda invoke --region=us-east-1 --function-name=`pulumi stack output lambda_name` output.txt
export('lambda_scan',  scan_fn.id)
export('lambda_rekognition',  lambda_rekognition.id)
# Export the name of the API endpoint
export('api_endpoint', scan_dep.invoke_url)
