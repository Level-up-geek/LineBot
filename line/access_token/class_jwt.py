from distutils.command.upload import upload
from turtle import Turtle
from jwcrypto import jwk
import jwt
from jwt.algorithms import RSAAlgorithm
from dotenv import load_dotenv
load_dotenv()
import time
import json
import os

"""公開鍵と秘密鍵の生成 and 秘密鍵で署名したJWTの生成"""
class Jwt:
    #これmainの方とpathはまとめたほうがよさそう。
    upload_private_key_path = './aws/s3/upload_file/assertion_private_key.json'
    upload_kid_path = './aws/s3/upload_file/kid.txt'

    #private_keyもkidもupload_fileにあるものとする
    def __init__(self):
        if os.path.isfile(Jwt.upload_private_key_path):
            self.__private_key = self.file_load(Jwt.upload_private_key_path)
            self.__kid = self.file_load(Jwt.upload_kid_path)
        else:
            self.__private_key = ""
            self.__kid = ""
            pass
    
    """
    基本は実行されることはない
    再発行の時は必要かも？
    """
    def create_assertion_key(self):
        if  not os.path.isfile(Jwt.upload_private_key_path):
            #Lineの規約に沿って
            key = jwk.JWK.generate(kty='RSA', alg='RS256', use='sig', size=2048)

            self.__private_key = key.export_private()
            self.create_file(Jwt.upload_private_key_path)
            
            public_key = key.export_public()
            print(public_key)
            self.__kid = input('公開鍵をLineDeveloper登録してkidを入力してください\n')
            self.create_file(Jwt.upload_kid_path)
            
            return True
        else:
            return False

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

    """"モジュールにした方がよさそう -> class_access_token.pyでも使ってるから"""   
    def create_file(self, upload_path):
            with open(upload_path, 'w+') as f:
                if upload_path == Jwt.upload_private_key_path:
                    json.dump(json.loads(self.__private_key), f, indent=2)    
                else:    
                    f.write(self.__kid)

    def file_load(self, download_path):
            with open(download_path, 'r') as f:
                return f.read()

