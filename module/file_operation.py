from distutils.command.upload import upload
from dotenv import load_dotenv
load_dotenv()
import os
import json

class FileOperation:
    
    upload_private_key_path = './aws/s3/upload_file/assertion_private_key.json'
    upload_kid_path = './aws/s3/upload_file/kid.txt'
    upload_access_token_path = './aws/s3/upload_file/access_token.json'
    upload_old_access_token_path = './aws/s3/upload_file/old_access_token.json'
    
    private_key_file_name = 'assertion_private_key.json'
    kid_file_name = 'kid.txt'
    access_token_file_name = 'access_token.json'

    """"ファイルの読み込み書き込みは例外が発生した時の処理書きたいね"""
    @classmethod
    def create_file(cls, upload_path, object):
        cls.check_exist(upload_path)
        with open(upload_path, 'w+') as f:
            if '.json' == os.path.splitext(upload_path)[1]:
                #res.json()でdict型になっている
                if type(object) is dict:
                    json.dump(object, f, indent=2)
                else:
                    json.dump(json.loads(object), f, indent=2)    
            else:    
                f.write(object)

    @classmethod
    def load_file(cls, load_path):
        cls.check_exist(load_path)
        with open(load_path, 'r') as f:
            if '.json' == os.path.splitext(load_path)[1]:
                return json.loads(f.read())
            else:
                return f.read()

    #アップロードパスのファイルが存在していなければ空で作る。
    #本当はこれらの関数をインスタンスメソッドにした方がいいんだけどね。initでcheckした方がいい。。
    @classmethod
    def check_exist(cls, path):
        if not os.path.isfile(path):
            file_path = os.path.dirname(path)
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            
            with open(path, 'w') as f:
                f.write('')
            return False

        return True