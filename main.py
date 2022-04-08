from importlib.resources import path
from msilib.schema import File
from os import access, getenv

from line.access_token.class_jwt import Jwt
from line.access_token.class_access_token import AccessToken
from aws.s3.class_s3 import S3 
from slack.class_slack import Slack 
from module.file_operation import FileOperation

from dotenv import load_dotenv
load_dotenv()

import sys, os

"""
アクセストークン周りの処理を実行する関数
・発行(jwt, アクセストークン)
・S3にアップロード、ダウンロード(jwt, アクセストークン)->アクセストークンをgithubへダウンロードするため
・アクセストークンの有効性の確認
  無効や期限が近付いていたら
  ・再発行
   ->slackに通知して、github actionsでkidを入力しに行く
  ・削除(古くなったアクセストークンを)
"""
bucket_name = os.getenv('AWS_S3_BUCKET_NAME')

def main(access_token, jwt, s3, slack, local_flag):
    #まずは、S3からアクセストークン
    s3.download_file(bucket_name, FileOperation.access_token_file_name, FileOperation.upload_access_token_path)
    
    if not os.path.isfile(FileOperation.upload_access_token_path) and local_flag:
    #アクセストークンをダウロード出来なかったとき用
        create_access_token_flow(access_token, jwt, s3, recreated_flag=False)
    else:
        print('アクセストークンをローカルで発行してください')
        sys.exit(1)
    
    #まずはアクセストークンを取得する
    access_token.token = FileOperation.load_file(FileOperation.upload_access_token_path)
    #アクセストークンが有効かどうか
    verify = access_token.verify()
    
    #local環境での実行の時
    if local_flag:
        if not verify:
            if input('アクセストークンの再発行を開始します。よろしいですか？\nyes/no\n') == 'yes':
                create_access_token_flow(access_token, jwt, s3, recreated_flag=True)
            
            if input('古くなったアクセストークンを削除します。いいですか?\nyes/no\n') == 'yes':
                access_token.old_token = FileOperation.load_file(FileOperation.upload_old_access_token_path)
                access_token.revoke()
    
    #git hub上で実行される場合(トークンの検証だけ行ってslackへ通知)
    else:
        slack.send_message(access_token.slack_message)   
    
def create_access_token_flow(access_token, jwt, s3, recreated_flag=False):
        jwt.create_assertion_key(recreated_flag)
                
        #バックアップとしてS3にprivate_keyとkidを保存しておく
        if not (s3.upload_file(FileOperation.upload_private_key_path, bucket_name, FileOperation.private_key_file_name) and  s3.upload_file(FileOperation.upload_kid_path, bucket_name, FileOperation.kid_file_name)):
            sys.exit(1)
            
        #アクセストークンで使うjwtをprivate_keyで署名して発行
        JWT = jwt.create()

        #JWTを利用してアクセストークンを発行する
        if access_token.create(JWT, recreated_flag):
            print('アクセストークンの作成に成功しました')
        else:
            print('アクセストークンの作成に失敗しました')

        if not s3.upload_file(FileOperation.upload_access_token_path, bucket_name, FileOperation.access_token_file_name):
            sys.exit(1)
        print('アクセストークンのs3へのアップロードが出来ました。')

def check_argv(local_flag):
    if local_flag.isdigit():
        return int(local_flag)
    else: 
        print('コマンドライン引数には0(local環境以外)か1(local環境)を入力してください。')
        sys.exit(1)



if __name__ == '__main__':
    #クラス間での連結度をできるだけ弱くしている
    access_token = AccessToken()
    s3 = S3()
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    slack = Slack(webhook_url)
    jwt = Jwt()

    
    local_flag = check_argv(sys.argv[1])
    #コマンドライン引数で特定のアクセストークンを消す処理が実行できるように(アクセストークンを渡す)
    main(access_token, jwt, s3, slack, local_flag)