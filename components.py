import pulumi
import mimetypes
import os
import json
from pulumi import FileAsset, ComponentResource
from pulumi_aws import s3, dynamodb


def dynamodb_table(table_name):
    return dynamodb.Table(
        table_name,
        attributes=[{
            "name": "Id",
            "type": "S"
        }],
        hash_key="Id",
        read_capacity=1,
        write_capacity=1)


def public_read_policy_for_bucket(bucket_name):
    return json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": "*",
            "Action": [
                "s3:GetObject"
            ],
            "Resource": [
                f"arn:aws:s3:::{bucket_name}/*",
            ]
        }]
    })


class StaticWebSite(ComponentResource):

    def __init__(self,
                 name: str,
                 content_dir: str,
                 index_document: str,
                 error_document: str,
                 opts: pulumi.ResourceOptions = None):

        super().__init__('StaticWebSite', name, None, opts)

        self.name = name
        self.s3_bucket = s3.Bucket(name,
                                   website={
                                       'index_document': index_document,
                                       'error_document': error_document
                                   })

        bucket_name = self.s3_bucket.id

        for file in os.listdir(content_dir):
            filepath = os.path.join(content_dir, file)
            mime_type, _ = mimetypes.guess_type(filepath)
            s3.BucketObject(file,
                            bucket=bucket_name,
                            source=FileAsset(filepath),
                            content_type=mime_type)

        s3.BucketPolicy("bucket-policy",
                        bucket=bucket_name,
                        policy=bucket_name.apply(public_read_policy_for_bucket))

        super().register_outputs({})
