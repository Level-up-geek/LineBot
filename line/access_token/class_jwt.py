from distutils.command.upload import upload
from turtle import Turtle
from jwcrypto import jwk
import jwt
from jwt.algorithms import RSAAlgorithm

from module.file_operation import FileOperation

from dotenv import load_dotenv
load_dotenv()

import os, sys, time

"""公開鍵と秘密鍵の生成 and 秘密鍵で署名したJWTの生成"""
class Jwt:
    """"Jwtクラスの変数は基本外部から書き換えられない"""

    #private_keyもkidもupload_fileにあるなら読み込む
    def __init__(self):
        if os.path.isfile(FileOperation.upload_private_key_path) and os.path.isfile(FileOperation.upload_kid_path):
            self.__private_key = FileOperation.load_file(FileOperation.upload_private_key_path)
            self.__kid = FileOperation.load_file(FileOperation.upload_kid_path)
        else:
            self.__private_key = ''
            self.__kid = ''
            
    """
    再発行の時やアクセストークンがS3から取得できなかったとき
    """
    def create_assertion_key(self, recreated_flag):
        #既に作成済みなら終了
        if os.path.isfile(FileOperation.upload_access_token_path):
            if recreated_flag:
                print('再発行を開始します\n')
            else:
                sys.exit(1)
        
        #Lineの規約に沿って
        key = jwk.JWK.generate(kty='RSA', alg='RS256', use='sig', size=2048)

        self.__private_key = key.export_private()
        FileOperation.create_file(FileOperation.upload_private_key_path, self.__private_key)
            
        public_key = key.export_public()
        print(public_key)

        #kidだけ他のメソッドに切り離す
        #access_token-workflowでkidに値代入からやりたいから
        self.__kid = input('公開鍵をLineDeveloper登録してkidを入力してください\n')
        FileOperation.create_file(FileOperation.upload_kid_path, self.__kid)
            
        return True
        
    def create(self):
        headers = {
            'alg': 'RS256',
            'typ': 'JWT',
            'kid': self.__kid
        }

        payload = {
            #.envを使うように
            'iss': os.getenv('LINE_CHANEL_ID'),
            'sub': os.getenv('LINE_CHANEL_ID'),
            'aud': 'https://api.line.me/',
            'exp':int(time.time())+(60 * 30),
            'token_exp': 60 * 60 * 24 * 30
        }
        key = RSAAlgorithm.from_jwk(self.__private_key)

        JWT = jwt.encode(payload, key, algorithm='RS256', headers=headers, json_encoder=None)
        return JWT