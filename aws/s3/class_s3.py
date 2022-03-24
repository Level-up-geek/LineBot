import logging
import boto3
from botocore.exceptions import ClientError
import os
from ..class_aws import Aws
class S3:
    client = Aws('s3')

    def upload_file(self, file_name, bucket_name, object_name=None):
        if object_name is None:
            object_name = os.path.basename(file_name)

        try:
            response = S3.client.s3_client.upload_file(file_name, bucket_name, object_name)
        except ClientError as e:
            logging.error(e)
            return False
        return True


    def download_file(self, bucket_name, object_name, file_name=None):
        if file_name is None:
            file_name = os.path.basename(object_name)

        try:
            response = S3.client.download_file(bucket_name, object_name, file_name)
        except ClientError as e:
            logging.error(e)
            return False
        return True
        