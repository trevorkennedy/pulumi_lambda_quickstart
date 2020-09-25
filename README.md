# Pulumi AWS Lambda Quickstart

## Overview
Pulumi is an open source infrastructre as code tool that allows developers to provision cloud resources using a progamming languages including (Python, JavaScript, Go and C#). It operates very similar to Terraform and CloudFormation only it is cloud agnostic and there are no YAML of JSON files to edit.

This quickstart will deploy:
- an S3 bucket configured to serve a static website
- a DynamoDB table
- a Lambda function to query the DynamoDB table
- a Lambda function which calls the Rekognition service (trigged by adding an image to the S3 bucket) with the resulting image label stored in DynamoDB

## Requirements
- [Python](https://www.python.org/downloads/) 3.7
- [AWS CLI](https://aws.amazon.com/cli/) 2.0
- [Pulumi](https://www.pulumi.com/docs/get-started/install/) 2.10

## Run
Issue the following commands to run and test:

```
pulumi config set aws:region us-west-2
pulumi up
curl $(pulumi stack output website_url)
aws s3 cp ~/Desktop/fireplace.jpg s3://$(pulumi stack output bucket_name)
aws s3 ls $(pulumi stack output bucket_name)
curl $(pulumi stack output api_endpoint)
```

## Cleanup
Use the following commands to teardown:

```
aws s3 rm s3://$(pulumi stack output bucket_name)/fireplace.jpg
pulumi destroy
```

## Architecture
![Architecture](https://raw.githubusercontent.com/trevorkennedy/pulumi_lambda_quickstart/master/Architecture.png)
