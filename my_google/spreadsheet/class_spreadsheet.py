from oauth2client.service_account import ServiceAccountCredentials
import gspread
import json

class SpreadSheet:
    
    def __init__(self, spreadsheet_key):
        self.__scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        self.__credentials = ServiceAccountCredentials.from_json_keyfile_name('my_google/secret/client_secret.json', self.__scope)
        self.__client = gspread.authorize(self.__credentials)
        self.__work = self.__client.open_by_key(spreadsheet_key)
    
    #汎用性は低いー＞元からesaの情報を書き込むだけのつもりだし
    def write(self, data):
        i = 0

        for user, user_data in data.items():
            #ワークシートリストの長さより大きいインデックス入れるとエラー起きてしまうので
            #例外処理をする
            if len(self.__work.worksheets()) - 1 < i:
                self.__work.add_worksheet(title=user, rows=365, cols=26)
            worksheet = self.__work.get_worksheet(i)

            #ユーザ名でシート判別でできるように
            if worksheet.title != user:
                worksheet.update_title(user)
            
            

            for date, posts_count in user_data.items():
                pass
            i += 1
