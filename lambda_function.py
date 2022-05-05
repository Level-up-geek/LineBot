import json
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
)

from linebot.models import ImageSendMessage

from dotenv import load_dotenv
load_dotenv()

import boto3, datetime, calendar

import logging, os, sys
from datetime import timedelta

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

channel_secret = os.getenv('LINE_SECRET_KEY', None)
channel_access_token = os.getenv('ACCESS_TOKEN', None)

if channel_secret is None:
    logger.error('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    logger.error('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

def lambda_handler(event, context):
    if not 'headers' in event:
        push_message(line_bot_api, os.getenv('LINE_GROUP_ID'), event['time'])
    else:
        if 'x-line-signature' in event['headers']:
            signature = event['headers']['x-line-signature']
        elif 'X-Line-Signature' in event['headers']:
            signature = event['headers']['X-Line-Signature']
        body = event['body']
        logging.debug(event)
        
        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            logger.error('Invalid signature. Please check your channel access token/channel secret.')
            return {'statusCode': 400}
    
    @handler.add(MessageEvent, message=TextMessage)
    def message(line_event):
        #text = line_event.message.text
        #line_bot_api.reply_message(line_event.reply_token, TextSendMessage(text=text))
        pass
    
    return {'statusCode': 200, 'body': ''}

def push_message(client, group_id, today):
    urls = get_signature_image_url(today)
    for url in urls:
        client.push_message(group_id, ImageSendMessage(original_content_url=url, preview_image_url=url))

def get_signature_image_url(today):
    s3 = boto3.client('s3')
    BUCKET = os.getenv('AWS_S3_BUCKET_NAME_FOR_DATA')
    KEY = ''
    data_prefixes = get_data_prefix(s3, BUCKET)
    today = get_today_date(today)
    year = today[0]
    month = today[1]
    week_name = today[2]
    keys = {
        'week': f'data_file/data_dir/{year}/{month}/{week_name}/posts_count_per_date.png',
        'month': f'data_file/data_dir/{year}/{month}/posts_count_per_date.png',
        'week-month': ''
    }
    week_month_flag = today[3]
    key_alt = keys[week_month_flag]
    signature_image_url = []

    #日曜日と月末が被った時
    #これだと、EventBridgeで週の分と月末の分で二回実行される。計6枚の画像が送られてしまう。
    #event['time']から、minuteを取得。そのminuteで週の分か月の分か判断できるようにする？　
    if week_month_flag == 'week-month':
        for data_dir in data_prefixes:
            for key in keys.values():
                if not key:
                    break
                
                KEY = key.replace('data_dir', data_dir)

                signature_image_url.append(s3.generate_presigned_url(
                    ClientMethod = 'get_object',
                    Params = {'Bucket' : BUCKET, 'Key' : KEY},
                    ExpiresIn = 3600,
                    HttpMethod = 'GET'
                ))
    else:
        for data_dir in data_prefixes:
            KEY = key_alt.replace('data_dir', data_dir)
            
            signature_image_url.append(s3.generate_presigned_url(
                ClientMethod = 'get_object',
                Params = {'Bucket' : BUCKET, 'Key' : KEY},
                ExpiresIn = 3600,
                HttpMethod = 'GET'
            ))

    return signature_image_url


def get_today_date(today: str) -> tuple:
    time = today.replace('Z', '+00:00')

    today = datetime.datetime.fromisoformat(time).date()
    tomorrow = today + timedelta(days=1)
    week_month_flag = 'week'

    if tomorrow.day == 1 and today.weekday() == 6:
        #月末と日曜が被っていたら line-push-event-month-ruleのeventは既にline-push-event-ruleで
        # すべて実行されるものはされているので実行しない。
        if datetime.datetime.fromisoformat(time).minute == 55:
            sys.exit(1)
        week_month_flag = 'week-month'
        
    elif tomorrow.day == 1:
        week_month_flag = 'month'
    

    week_on_number = {
        0: 'first_week',
        1: 'second_week',
        2: 'third_week',
        3: 'fourth_week',
        4: 'fifth_week'

    }

    c = calendar.Calendar(0)
    calendar_list = c.monthdatescalendar(today.year, today.month)
    week_list = [[i, week_list] for i, week_list in enumerate(calendar_list) if today in week_list ]
    week_number = week_list[0][0]

    return today.year, today.month, week_on_number[week_number], week_month_flag

def get_data_prefix(s3, BUCKET):
    res = s3.list_objects(Bucket=BUCKET, Prefix='data_file/', Delimiter="/")
    prefixes = res['CommonPrefixes']
    data_prefixes = []

    for prefix in prefixes:
        data_prefixes.append(prefix['Prefix'].split('/')[1])

    return data_prefixes