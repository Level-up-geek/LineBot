from smtplib import SMTP_SSL
from dotenv import load_dotenv
load_dotenv()

from module.file_operation import FileOperation as fo
from pandas.core.common import flatten

import esa

import sys, datetime, logging, os, calendar
import pandas as pd
import matplotlib.pyplot as plt

logger = logging.getLogger()
logger.setLevel(logging.ERROR)

def main(all_get_flag, week_or_month_flag):
    team_name = os.getenv('ESA_TEAM_NAME')
    today = datetime.date(2022, 4, 30)
    week_number = 0

    if week_or_month_flag == 'week':        
        c = calendar.Calendar(0)
        calendar_list = c.monthdatescalendar(today.year, today.month)
        #MEMO:今週分を抽出・Lambda側でもグラフを取り出すさいに使う。
        week_list = [[i, week_list] for i, week_list in enumerate(calendar_list) if today in week_list ]
        #mothdatecalendarのlistの要素番号が週番号と見立てた。
        week_number = week_list[0][0]
        query_date = week_list[0][1]
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
    week_on_number = {
        0: 'first_week',
        1: 'second_week',
        2: 'third_week',
        3: 'fourth_week',
        4: 'fifth_week'
    }

    if week_or_month_flag == 'month':
        csv_file_path = f'csv/member/{year}/{month}/posts_count_per_date.csv'
        create_csv(result, csv_file_path, year, month)
    else:
        csv_file_path = f'csv/member/{year}/{month}/{week_on_number[week_number]}/posts_count_per_date.csv'
        create_csv(result, csv_file_path, year, month)


"""
csvファイルを作成する
グラフを作る関数を呼び出す
"""
def create_csv(data, csv_file_path_alt, year, month):
    for member in data.keys():
        date_list = []
        csv_file_path = csv_file_path_alt.replace('member', member)
        for month, posts_count_per_day in  reversed(data[member][year].items()):
            [date_list.append([day, count]) for day, count in posts_count_per_day.items()]
        
        df = pd.DataFrame(date_list, columns=['Date', 'PostCount'])
        df.to_csv(fo.check_exist(csv_file_path), index=False)
        df.plot(x='Date')
        plt.show()
        sys.exit(1)   

"""
標準入力のチェック
"""
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