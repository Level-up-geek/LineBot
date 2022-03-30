import os
from xmlrpc.client import ResponseError
from slack_sdk.webhook import WebhookClient

class Slack:
    def __init__(self, webhook_url):
        self.__webhook = WebhookClient(webhook_url)

    def send_message(self, message):
        response = self.__webhook.send(text=message)
        return response

    