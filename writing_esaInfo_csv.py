from cProfile import label
from dotenv import load_dotenv
load_dotenv()

from module.file_operation import FileOperation as fo
from pandas.core.common import flatten

import esa

import sys, datetime, logging, os, calendar
import pandas as pd
import matplotlib.pyplot as plt
import japanize_matplotlib

logger = logging.getLogger()
logger.setLevel(logging.ERROR)

def main(all_get_flag, week_or_month_flag):
    team_name = os.getenv('ESA_TEAM_NAME')
    #MEMO:todayにしないと、Git Hub Actionsで実行された時の日付が取得できない
    today = datetime.date(2022, 4, 10)
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
        csv_file_path = f'data_file/member/{year}/{month}/posts_count_per_date.csv'
        create_csv(result, csv_file_path, year, month)
    else:
        csv_file_path = f'data_file/member/{year}/{month}/{week_on_number[week_number]}/posts_count_per_date.csv'
        create_csv(result, csv_file_path, year, month)


"""
csvファイルを作成する
グラフを作る関数を呼び出す
"""
def create_csv(data, csv_file_path_alt, year, month):
    comparison_source_ax = None
    #MEMO:memberが増えると、member同士の比較は修正しないとむり。
    for member in data.keys():
        date_list = []
        monthes = []
        csv_file_path = csv_file_path_alt.replace('member', member)
        for month, posts_count_per_day in  reversed(data[member][year].items()):
            [date_list.append([day, count]) for day, count in posts_count_per_day.items()]
            monthes.append(month)

        df = pd.DataFrame(date_list, columns=['日付け', '投稿数'])
        df.to_csv(fo.check_exist(csv_file_path), index=False)
        
        x_label = '日付け'
        y_label = '投稿数'
        
        #比較図の作成
        if comparison_source_ax is not None:
            title = f'比較: {monthes[0]}/{date_list[0][0]}日-{monthes[-1]}/{date_list[-1][0]}日の投稿数推移'
            comparison_distination_df = df.rename(columns={'投稿数': f'{member}の投稿数'})
            comparison_distination_df.plot(title=title, x=x_label, color='r', label=member, ylim=(0, 3), ax=comparison_source_ax)

            image_file_path = csv_file_path.replace('.csv', '.png').replace(member, 'comparison')
            plt.savefig(fo.check_exist(image_file_path), dpi=300)
            
        title = f'{member} {monthes[0]}/{date_list[0][0]}日-{monthes[-1]}/{date_list[-1][0]}日の投稿数推移'
    
        ax = df.plot(title=title, yticks=[0, 1, 2, 3], x=x_label, color='pink', ylim=(0, 3), label=member)
        ax.set_xlabel(xlabel=x_label)
        ax.set_ylabel(ylabel=y_label, labelpad=15, rotation = 'horizontal')
        #MEMO: 月のグラフは週ごと(1~7, 8~15, 16~23, 24~31)の合計を出してそのグラフで
        #あと、前週との比較は棒グラフにするか、user同士とか
        # df. plot.bar()
        image_file_path = csv_file_path.replace('.csv', '.png')
        #dpiは1ピクセルにどのくらいのドットで表すか。デフォは100
        plt.savefig(fo.check_exist(image_file_path), dpi=300)

        if comparison_source_ax is None:
            comparison_source_df = df.rename(columns={'投稿数': f'{member}の投稿数'})
            comparison_source_ax = comparison_source_df.plot(title=title, yticks=[0, 1, 2, 3], x=x_label, color='b', ylim=(0, 3), label=member)

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

"""
実行時引数として以下の二つが必要
・全記事取得か月ごと、週間ごとに取得か(1 or 0)
・月ごとか週間ごとのグラフを取得か(month or week)
"""
if __name__ == '__main__':
    all_get_flag = check_digit_argv(sys.argv[1])
    week_or_month_flag = check_str_argv(sys.argv[2])
    main(all_get_flag, week_or_month_flag)