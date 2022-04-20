from dotenv import load_dotenv
load_dotenv()

from module.file_operation import FileOperation as fo
from pandas.core.common import flatten

import esa

import sys, datetime, logging, os, calendar
import pandas as pd

def main(all_get_flag, week_or_month_flag):
    #MEMO: 環境変数に入れるかいれないか
    team_name = os.getenv('ESA_TEAM_NAME')
    today = datetime.date(2022, 3, 27)
    if week_or_month_flag == 'week':        
        c = calendar.Calendar(0)
        calendar_list = c.monthdatescalendar(today.year, today.month)
        
        #今週分を抽出
        week_list = [week_list for week_list in calendar_list if today in week_list ]
        print(week_list)
        query_date = week_list[0]
    else:
        c = calendar.monthcalendar(year=today.year, month=today.month)
        day_list = [day for day in list(flatten(c)) if day != 0]        
        query_date = [datetime.date(today.year, today.month, day_list[0]).strftime('%Y-%m-%d'), datetime.date(today.year, today.month, day_list[-1]).strftime('%Y-%m-%d')]
            
    #esaにあるユーザごとの日付ごとの記事投稿数を取得
    if all_get_flag:
        result = esa.get_all_posts(team_name)
    else:
        result = esa.get_posts(query_date, team_name, week_or_month_flag)

    year = str(today.year)
    month = str(today.month)

    if week_or_month_flag == 'month':
        create_csv_per_month(result, year, month)
    else:
        create_csv_per_week(result,  year, month)

def create_csv_per_month(data, year, month):
    for member in data.keys():
        csv_file_path = f'csv/{member}/{year}/{month}/posts_count_per_date.csv'
        data_list = [[day, count] for day, count in data[member][year][month].items()]

        df = pd.DataFrame(data_list, columns=['Date', 'PostCount'])
        df.to_csv(fo.check_exist(csv_file_path), index=False)
        

    
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