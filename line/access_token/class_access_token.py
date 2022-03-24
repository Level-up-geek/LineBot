import urllib.parse
import requests
import json

class AccessToken:
    upload_path = './aws/s3/upload_file/access_token.txt'
    __access_token = ""

    #setter
    def set(self, access_token):
        self.__access_token = access_token


    #アクセストークン作成
    def create(self, JWT):
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
        #ここから、access_token取り出すか、ファイルに全部保存してS3に保存するか
        object = res.json()
        self.__access_token = object['access_token']
        
        self.create_file()
        return True

    #アクセストークンの有効性の確認
    #def verify(self):

    #不要になったアクセストークン削除
    #def revoke(self):

        
    def create_file(self):
            with open(AccessToken.upload_path, 'w+') as f:
                f.write(self.__access_token)

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


    