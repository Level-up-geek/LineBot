import logging
import boto3
from botocore.exceptions import ClientError
import os, json
from ..class_aws import Aws
from module.file_operation import FileOperation

class S3(Aws):
    def __init__(self, service_name):
        super().__init__(service_name)

    def upload_file(self, file_name, bucket_name, object_name=None):
        if object_name is None:
            object_name = os.path.basename(file_name)

        try:
            with open(file_name, 'rb') as fr:
                response = self.s3_client.put_object(Body=fr.read(), Bucket=bucket_name, Key=object_name)
        except ClientError as e:
            logging.error(e)
            return False
        return True


    def download_file(self, bucket_name, object_name, file_name=None):
        if file_name is None:
            file_name = os.path.basename(object_name)

        try:
            #get_object()->dict(jsonではなくて、dict。)
            response = self.s3_client.get_object(Bucket=bucket_name, Key=object_name)
        except ClientError as e:
            logging.error(e)
            return False

        #read()でバイナリーデータになる。read()ストリーミング型ではなくなる。これは、iteratorみたいな感じかな。
        body = response['Body'].read()
        #バイナリーデータから文字列へ
        access_token = body.decode()
        
        #自分でファイルに読み込まないといけなくなった。
        #本当にファイルにする必要があるのか？ー＞アップロードしないとか、、
        FileOperation.create_file(FileOperation.upload_access_token_path , json.loads(access_token))
        