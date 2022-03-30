from module.file_operation import FileOperation
from dotenv import load_dotenv
load_dotenv()

import urllib.parse,  requests, json, os

class AccessToken:
    
    def __init__(self):
        self.__token = {}
        self.__old_token = {}
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
            #slackへ送るメッセージどこで定義するか、、
            #slackへ送るsend_messageメソッドをどこで使うか。
            #verifyメソッドの戻り値はtrue, falseがいいけどなあ 
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

        if pass_time.day < 3:
            #slackにactionsのurlを通知して更新作業を開始させる。
            # slack webhook url: https://hooks.slack.com/services/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
            #https://github.com/Level-up-geek/LineBot/actions/runs/{github.run_id}
            #github.run_idはpython main.py ${{github.run_id}}で渡す。
            #slackクラスはこのメソッドの中だけで使うよう、このメソッドの中でimportする
            self.__message = 'アクセストークンの有効期限が近づいています。\n再発行してください。'
            return False
        
        self.__message = f'有効期限は残り{pass_time.day}日です。このアクセストークンは有効です。\n'
        return True

    #MEMO:
    #S3からアクセストークンを読み取る。
    #レスポンスによって、アクセストークンの発行が1回目の処理か2回目以降の処理になるか分岐
    #1回目
     #鍵の作成にjwtの作成
     #アクセストークン発行
     #S3へアップロード(アクセストークンもjwtも)
    #2回目
     #有効性を確認する
     #有効の場合
      #何もしない
     #期限が近づいていたら
      #S3から署名付きjwtを読み込む。
      #アクセストークンを再発行する。
      #前のアクセストークンを削除する
      #新たなアクセストークンを書き込む
    #(これ、pull requestがclosedになった時だけじゃだめじゃない?)
    #cronにして、29日後とかに再発行するプログラムを実行するようにしないと。
    
    ###別ワークフロー(アクセストークン発行ワークフロー)でこのコードを実行する(https://developer.mamezou-tech.com/blogs/2022/03/08/github-actions-reuse-workflows/)
    ###このコードを実行するワークフローはcronでの定期的実行と、データの受け渡し(別ワークフローからworkflow_call)と複数イベントある(https://tech.anti-pattern.co.jp/github-actions-notorigaibento/)
    ###stepの中でif分使えばイベントごとに処理を変更できる   if: github.event.schedule != '30 5 * * 1,3'(https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#schedule)
    
    ###jwtやアクセストークンは発行したらS3にアップロード(もちろんプライベートなバケットへ)
    ###S3からjwtを取得してアクセストークンを再発行してそのアクセストークンをS3-Lambda-deploy-workflow.ymlに渡す。
     
    ###ちなみに、アクセストークンをどのように渡すかー＞ echo "::set-output name=line_access_token::$(echo python access_token.py)"、
    ###call-workflow-passing-data:
    ###uses: .github/workflows/S3-Lambda-deploy-workflow.yml
    ###with:
    ###  line_access_token: ${{ steps.id.outputs.line_access_token }}
    ### S3-Lambda-deploy-workflowではアクセストークンをS3から取得してもいいが、
    ### リクエスト数や、通信の時間を考えれば無駄な気がするのでとgithub actions内(アクセストークンー＞デプロイと一連のワークフロー連携として)で収める。
    ###また、S3は重要なデータのバックアップにも適しているためS3へのアップロードは無駄ではない。

    #s3 = S3()
    #s3.upload_file()

    
    #kid
    #3798726f-61fd-43f0-b2ef-21091a714be2

    #再発行する際に、jwtが必要
    #そのjwtの署名をするのに秘密鍵が必要。
    #つまり秘密鍵はGitHub上で保管しておくか
    #GitHubは最大でも90日間、、
    #S3に保存しておいて、そこから取得してくるか。


    