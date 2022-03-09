# LineBot
LineBotで色々なことがLineを使って完結できるようにするー＞便利に楽にみんなで楽しめるようなLineにする

# 環境構築
```
git clone git@github.com:Level-up-geek/LineBot.git
```
venvで開発環境をそろえる。(lambdaでpython3.9なのでバージョン合わせる)
```
py -3.9 -m venv venv
```
仮想環境に入る
```
cd venv/Scripts
activate.bat
```
※powershellの場合はできなかったので、とりあえずはコマンドプロンプトで行う

開発環境をそろえるため同じパッケージをインストール
```
pip install -r requirements.txt
```

開発環境の構築完了

# zipにする方法
lambdaにアップロードするpackagesディレクトリを作成する(この中にパッケージとlambda_function.pyを入れる)
```
mkdir packages
```
```
cd packages
```
lambda_function.pyをpackagesにコピーしてくる
```
cp ../lambda_function.py lambda_function.py
```
lambdaでも同じパッケージを使うためにpackagesの中にrequirements.txtからインストールする
```
 pip install -r ../require.text -t ./
 ```
 最後に、packagesをzipにする。(注意なのが、lambdaにアップロードするのはpackagesの中身だけ。packagesディレクトリごとやらない)
 powershellの場合
 ```
 compress-archive packages/* dst
 ```
 後はアップロードしに行くだけ。これから、githubからlambdaに自動アップロードができるようにしたい。

