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

    @classmethod
    def create_file(cls, upload_path, object):
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
        with open(load_path, 'r') as f:
            if '.json' == os.path.splitext(load_path)[1]:
                return json.loads(f.read())
            else:
                return f.read()
