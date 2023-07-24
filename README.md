# LineBot
このアプリについて詳しい仕様は以下を参考に（結構雑に書いています）。
https://esa-pages.io/p/sharing/18982/posts/103/bdd36da6182071c313b5.html

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
