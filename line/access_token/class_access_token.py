from module.file_operation import FileOperation
from dotenv import load_dotenv
load_dotenv()

import urllib.parse,  requests, json, os

class AccessToken:
    
    def __init__(self):
        self.__token = {}
        self.__old_token = {}
        #slackへ通知するためのメッセージ
        self.__message = ''

    @property
    def token(self):
        return self.__token
    
    @token.setter
    def token(self, token):
        if type(token) is dict:
            self.__token = token
        else:
            raise ValueError('正しい値を入れてください')

    @property
    def old_token(self):
        return self.__old_token
    
    @old_token.setter
    def old_token(self, old_token):
        if type(old_token) is dict:
            self.__old_token = old_token
        else:
            raise ValueError('正しい値を入れてください')

    @property
    def slack_message(self):
        print(self.__message)
        return self.__message
    
    


    #アクセストークン作成
    def create(self, JWT, recreated_flag):
        #古いトークンを削除する時に使うので残しておく。
        if recreated_flag:
            FileOperation.create_file(FileOperation.upload_old_access_token_path, self.__token)

        url = 'https://api.line.me/oauth2/v2.1/token'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        body = {
            'grant_type': 'client_credentials',
            'client_assertion_type': 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
            'client_assertion': JWT
        }
        
        res = requests.post(url, params=body, headers=headers)
        
        if res.status_code == 200:
            self.__token = res.json()
            FileOperation.create_file(FileOperation.upload_access_token_path, self.__token)            
            return True
        else:
            res.raise_for_status()
            return False

    #アクセストークンの有効性の確認
    def verify(self):
        url = 'https://api.line.me/oauth2/v2.1/verify'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        body = {
            'access_token': self.__token['access_token']
        }

        res = requests.get(url, params=body, headers=headers)

        if res.status_code == 200:
            return self.__check_expires(res.json())
        else:
            #主にエラーの時
            print(res.json())
            return False


    #不要になったアクセストークン削除
    def revoke(self):
        url = 'https://api.line.me/oauth2/v2.1/revoke'
        body = {
            'client_id': os.getenv('LINE_CHANEL_ID'),
            'client_secret': os.getenv('LINE_CHANEL_SECRET'),
            'access_token': self.__old_token['access_token']
        }
        
        res = requests.post(url, data=body)

        if res.status_code == 200:
            print('トークンの削除に成功しました。')
        else:
            print(res.json())
    
    #アクセストークンが有効期限内かどうか
    def __check_expires(self, verify_object):
        import datetime
        pass_time = datetime.datetime.fromtimestamp(verify_object['expires_in'])

        if pass_time.day <= 3:
            self.__message = 'アクセストークンの有効期限が近づいています。\n再発行してください。\n詳しくはslackのピン止めを確認してください。'
            return False
        
        self.__message = f'有効期限は残り{pass_time.day}日です。このアクセストークンは有効です。\n'
        return True


    