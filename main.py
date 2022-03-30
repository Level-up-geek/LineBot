from importlib.resources import path
from os import getenv

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
    
    if not os.path.isfile(FileOperation.upload_access_token_path):
    #アクセストークンをダウロード出来なかったとき用
        create_access_token_flow(access_token, jwt, s3, recreated_flag=False)
    else:
    #2回目以降の処理
        #まずはアクセストークンを取得する
        access_token.token = FileOperation.load_file(FileOperation.upload_access_token_path)
        #アクセストークンが有効かどうか
        verify = access_token.verify()
        if local_flag:
            if not verify:
                create_access_token_flow(access_token, jwt, s3, recreated_flag=True)
            #ここから、古いアクセストークンをrevokeしに行く。
            # Lineのsecretとidが必要
            # status codeが200だったらold_access_tokenファイルも削除する。
        else:
            #GitHub上からslackへ通知してくれる
            res = slack.send_message(access_token.slack_message)
            print(f'status: {res.status_code} body: {res.body}')
        
        
    #boto3は.aws/configureにアクセスのための秘匿情報を入れる必要があることに注意
        
#再発行は、1から作り直しカモ、リフレッシュトークンないし。
#秘密鍵から作るかぁ。。
#recreate_flag=Trueならjwt.create_assertion_keyを実行するようにするか。

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

def check_argv(local_flag):
    if local_flag.isdigit():
        return int(local_flag)
    else: 
        print('コマンドライン引数には0(local環境以外)か1(local環境)を入力してください。')
        sys.exit(1)



if __name__ == '__main__':
    #クラス間での連結度をできるだけ弱くしている
    access_token = AccessToken()
    jwt = Jwt()
    s3 = S3()
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    slack = Slack(webhook_url)
    #コマンドライン引数が整数かどうか
    local_flag = check_argv(sys.argv[1])
    main(access_token, jwt, s3, slack, local_flag)