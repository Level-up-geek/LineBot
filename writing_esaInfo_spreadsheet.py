from my_google.spreadsheet.class_spreadsheet import SpreadSheet

import esa

import sys, datetime
 

def main(all_get_flag):
    #MEMO: 環境変数に入れるかいれないか
    team_name = 'level-up-geek'

    #esaにあるユーザごとの日付ごとの記事投稿数を取得
    if all_get_flag:
        result = esa.get_all_posts(team_name)
    else:
        query_date = str(datetime.date.today())
        result = esa.get_posts(query_date, team_name)
    
    spreadsheet_key = '1MNhqVd8PhYp0rjVx6fYdJDKl2Bxfe1KKoCp6PWkdDBU'
    spreadsheet = SpreadSheet(spreadsheet_key)

    spreadsheet.write(result)
   


def check_argv(local_flag):
    if local_flag.isdigit():
        return int(local_flag)
    else: 
        print('コマンドライン引数には0(local環境以外)か1(local環境)を入力してください。')
        sys.exit(1)

if __name__ == '__main__':
    all_get_flag = check_argv(sys.argv[1])
    main(all_get_flag)