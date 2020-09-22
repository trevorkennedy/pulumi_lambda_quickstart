from pulumi_aws import config, iam

lambda_role = iam.Role('lambdaRole',
    assume_role_policy="""{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": "sts:AssumeRole",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Effect": "Allow",
                "Sid": ""
            }
        ]
    }"""
)

# Give lambda fuctions access to S3, DynamoDB and Rekognition
lambda_role_policy = iam.RolePolicy('lambdaRolePolicy',
    role=lambda_role.id,
    policy="""{
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "s3:*",
                "dynamodb:PutItem",
                "dynamodb:Scan",
                "rekognition:*"
            ],
            "Resource": "*"
        }]
    }"""
)