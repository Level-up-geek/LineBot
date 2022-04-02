import sys
from xmlrpc.client import ResponseError
from slack_sdk.webhook import WebhookClient

class Slack:
    def __init__(self, webhook_url):
        self.__webhook = WebhookClient(webhook_url)

    def send_message(self, message):
        res = self.__webhook.send(text=message)
        print(f'status: {res.status_code} body: {res.body}')
        if not res.status_code == 200:
            sys.exit(1)

    