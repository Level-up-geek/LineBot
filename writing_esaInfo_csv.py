from dotenv import load_dotenv
load_dotenv()

from typing import get_type_hints

import esa

import sys, datetime, logging, os
import pandas as pd

def main(all_get_flag, week_or_month_flag):
    #MEMO: 環境変数に入れるかいれないか
    team_name = os.getenv('ESA_TEAM_NAME')
    query_date = datetime.date.today()
        
    #esaにあるユーザごとの日付ごとの記事投稿数を取得
    if all_get_flag:
        result = esa.get_all_posts(team_name)
    else:
        result = esa.get_posts(str(query_date), team_name)

    year = str(query_date.year)
    month = str(query_date.month)
    week = query_date.weekday()

    if week_or_month_flag == 'month':
        create_csv_per_month(result, year, month)
    else:
        create_csv_per_week(result,  year, month, week)
""" {user: {
    year: {
        month: {
            day: count
            }
        }
    }
}
 """
def create_csv_per_month(data, year, month):
    for member in data.keys():
        data_list = [[day, count] for day, count in data[member][year][month].items()]
        df = pd.DataFrame(data_list, columns=['Date', 'PostCount'])
        print(df)

    
def create_csv_per_week(data, year, month, week_number):
    print('')
   


def check_digit_argv(all_get_flag):
    if all_get_flag.isdigit():
        return int(all_get_flag)
    else: 
        logging.error('コマンドライン引数には0(local環境以外)か1(local環境)を入力してください。')
        sys.exit(1)

def check_str_argv(week_or_month_flag):
    if week_or_month_flag == 'month' or week_or_month_flag == 'week':
        return week_or_month_flag
    else:
        logging.error('weekかmonthを入力してください')
        sys.exit(1)

if __name__ == '__main__':
    all_get_flag = check_digit_argv(sys.argv[1])
    week_or_month_flag = check_str_argv(sys.argv[2])
    main(all_get_flag, week_or_month_flag)