import boto3

class Aws:
    def __init__(self, service_name):
        self.s3_client = boto3.client(service_name)