from importlib.resources import path
from os import getenv
from line.access_token.class_jwt import Jwt
from line.access_token.class_access_token import AccessToken
from aws.s3.class_s3 import S3 
from dotenv import load_dotenv
load_dotenv()
import sys, os

"""
アクセストークン周りの処理を実行する関数
・発行(jwt, アクセストークン)
・S3にアップロード、ダウンロード(jwt, アクセストークン)
・アクセストークンの有効性の確認
・再発行
・削除
"""
def main(access_token, jwt, s3):
    upload_key_path = './aws/s3/upload_file/assertion_public_key.json'
    upload_kid_path = './aws/s3/upload_file/kid.txt'
    upload_access_token_path = './aws/s3/upload_file/access_token.txt'
    
    bucket_name = os.getenv('AWS_S3_BUCKET_NAME')
    
    key_file_name = 'assertion_private_key.json'
    kid_file_name = 'kid.txt'
    access_token_file_name = 'access_token.txt'

    #LineDeveloperで公開鍵を登録すると入手できる
    
    
    if jwt.create_assertion_key():
    #1回目なのでアクセストークン発行の処理
        #アクセストークンで使うjwtをprivate_keyで署名して発行
        JWT = jwt.create()

        #バックアップとしてS3にprivate_keyとkidを保存しておく
        if not s3.upload_file(upload_key_path, bucket_name, access_token_file_name) and  s3.upload_file(upload_kid_path, bucket_name, kid_file_name):
            sys.exit(1)

        #JWTを利用してアクセストークン発行する
        if access_token.create(JWT):
            print('アクセストークンの作成に成功しました')

        if not s3.upload_file(upload_access_token_path, bucket_name, key_file_name):
            sys.exit(1)

    else:
    #2回目以降の処理    
        #まずはアクセストークンを取得する
        access_token.token = download_file(upload_access_token_path)
        
        
        #2回目以降なのでアクセストークンの有効性を見る
        #再発行って、同じprivate_keyとkidでいけるかな？
        #できたら、response.json()を要確認(ちゃんと有効期限が30日になっているか)
        #削除の時、古いアクセストークンけす。a.pyにはっつけてある
    #最後に最終的なaccess_token.txtを出力する
    #そして次のワークフロー(S3-Lambda-deploy)へアクセストークンを渡す
    #boto3は.aws/configureにアクセスのための秘匿情報を入れる必要があることに注意
        


""""いずれは、class_access_tokenやclass_jwtの中にあるdownload_fileなどのファイル操作はモジュールにしたい"""
def download_file(path):
    with open(path, 'r') as f:
        return f.read()


if __name__ == '__main__':
    #クラス間での連結度をできるだけ弱くしている
    access_token = AccessToken()
    jwt = Jwt()
    s3 = S3()
    main(access_token, jwt, s3)