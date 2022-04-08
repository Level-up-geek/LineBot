import logging
import boto3
from botocore.exceptions import ClientError
import os
from ..class_aws import Aws
class S3(Aws):
    def __init__(self, service_name):
        super().__init__(service_name)

    def upload_file(self, file_name, bucket_name, object_name=None):
        if object_name is None:
            object_name = os.path.basename(file_name)

        try:
            response = self.s3_client.upload_file(file_name, bucket_name, object_name)
            print(response)
        except ClientError as e:
            logging.error(e)
            return False
        return True


    def download_file(self, bucket_name, object_name, file_name=None):
        if file_name is None:
            file_name = os.path.basename(object_name)

        try:
            response = self.s3_client.download_file(bucket_name, object_name, file_name)
        except ClientError as e:
            logging.error(e)
            return False
        return response
        