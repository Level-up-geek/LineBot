from dotenv import load_dotenv
import numpy as np
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
    today = datetime.date.today()
    #today = datetime.date(2022, 12, 18)
    week_number = 0

    if week_or_month_flag == 'week':        
        c = calendar.Calendar(0)
        calendar_list = c.monthdatescalendar(today.year, today.month)
        week_list = [[i, week_list] for i, week_list in enumerate(calendar_list) if today in week_list ]
        #mothdatecalendarのlistの要素番号が週番号と見立てた。
        week_number = week_list[0][0]
        query_date = week_list[0][1]
    elif week_or_month_flag == 'month':
        c = calendar.monthcalendar(year=today.year, month=today.month)
        day_list = [day for day in list(flatten(c)) if day != 0]        
        query_date = [datetime.date(today.year, today.month, day_list[0]).strftime('%Y-%m-%d'), datetime.date(today.year, today.month, day_list[-1]).strftime('%Y-%m-%d')]
    else:
        query_date = today.year
    
    try:
        #esaにあるユーザごとの日付ごとの記事投稿数を取得
        if all_get_flag:
            result = esa.get_all_posts(team_name)
        else:
            result = esa.get_posts(query_date, team_name, week_or_month_flag)
    except KeyError as e:
        logger.error(f"{e}月は投稿されていいないのでグラフは作成できません。")
        exit()

    year = str(today.year)
    month = str(today.month)
    week_on_number = {
        0: 'first_week',
        1: 'second_week',
        2: 'third_week',
        3: 'fourth_week',
        4: 'fifth_week',
        5: 'six_week'
    }

    if week_or_month_flag == 'month':
        csv_file_path = f'data_file/member/{year}/{month}/posts_count_per_date.csv'
        create_csv(result, csv_file_path, year, month)
    elif week_or_month_flag == 'week':
        csv_file_path = f'data_file/member/{year}/{month}/{week_on_number[week_number]}/posts_count_per_date.csv'
        create_csv(result, csv_file_path, year, month)
    else:
        csv_file_path = f'data_file/member/{year}/posts_count_per_date.csv'
        create_csv(result, csv_file_path, year, month, one_year_graph_flag=True)



"""
csvファイルを作成する
グラフを作る関数を呼び出す
get_all_postsで取得した場合のresultには対応していない。
#TODO:1年分のグラフ作成の処理は1週間や1カ月のグラフと一緒にしているが分けたほうが良い。
"""
def create_csv(data, csv_file_path_alt, year, month, one_year_graph_flag=False):
    #日本語表示できるように
    comparison_source_ax = None
    #MEMO:memberが増えると、member同士の比較は修正しないとむり。
    for member in data.keys():
        date_list = []
        monthes = []
        csv_file_path = csv_file_path_alt.replace('member', member)
        if not one_year_graph_flag:
            for month, posts_count_per_day in  reversed(data[member][year].items()):
                [date_list.append([day, count]) for day, count in posts_count_per_day.items()]
                monthes.append(month)
        else:
            for month, posts_count_per_day in  reversed(data[member][year].items()):
                date_list.append([month, sum(posts_count_per_day.values())])
                monthes.append(month)

        df = pd.DataFrame(date_list, columns=['日付け', '投稿数'])
        df.to_csv(fo.check_exist(csv_file_path), index=False)
        
        x_label = '日付け'
        y_label = '投稿数'
        xticks = None
        yticks = [0, 1, 2, 3, 4]
        ylim = (0, 4)
        xlim = None
        dpi = 300

        if one_year_graph_flag:
            yticks = np.arange(0, 40, step=3)
            ylim = (0, 40)
            xticks = np.arange(1, 13, step=1)
            xlim = (1, 12)

        #月のグラフはx目盛り2日ごと(indexで指定)
        if len(date_list) >= 8 and not one_year_graph_flag:
            start = 0
            end = int(date_list[-1][0]) + 1
            xticks = np.arange(start, end, step=2)
            xlim = ([xticks[0], xticks[-1]])
        
        #比較図の作成(2人用)
        if comparison_source_ax is not None:
            if not one_year_graph_flag:
                comparison_title = f'比較: {monthes[0]}/{date_list[0][0]}日-{monthes[-1]}/{date_list[-1][0]}日の投稿数推移'
            else:
                comparison_title = f'比較: {monthes[0]}月-{monthes[-1]}月の投稿数推移'

            comparison_distination_df = df.rename(columns={'投稿数': f'{member}の投稿数'})
            comparison_distination_df.plot(title=comparison_title, x=x_label, color='r', label=member, ylim=ylim, ax=comparison_source_ax)

            image_file_path = csv_file_path.replace('.csv', '.png').replace(member, 'comparison')
            plt.savefig(fo.check_exist(image_file_path), dpi=dpi)
            
        if not one_year_graph_flag:
            title = f'{get_member_name(member)}の{monthes[0]}/{date_list[0][0]}日-{monthes[-1]}/{date_list[-1][0]}日の投稿数推移'
        else:
            title = f'{get_member_name(member)}の{year}年度{monthes[0]}月-{monthes[-1]}月の投稿数推移'
    
        ax = df.plot(title=title, yticks=yticks, xticks=xticks, xlim=xlim , x=x_label, color='pink', ylim=ylim, label=member)
        ax.set_xlabel(xlabel=x_label)
        ax.set_ylabel(ylabel=y_label, labelpad=15, rotation = 'horizontal')

        image_file_path = csv_file_path.replace('.csv', '.png')
        plt.savefig(fo.check_exist(image_file_path), dpi=dpi)

        if comparison_source_ax is None:
            comparison_source_df = df.rename(columns={'投稿数': f'{member}の投稿数'})
            comparison_source_ax = comparison_source_df.plot(title=title, yticks=yticks, xticks=xticks, xlim=xlim, x=x_label, color='b', ylim=ylim, label=member)

""" 
グラフに名前を表示する際に、esaに登録してある名前ではなくニックネームに変える
esaの名前はなんかローマ字で分かりにくい

"""
def get_member_name(esa_name):
    member_list = {'haruya_nagai': 'はるやー','satoru_iwawaki': 'さとるー'}
    return member_list[esa_name]

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
    if week_or_month_flag == 'month' or week_or_month_flag == 'week' or week_or_month_flag == 'year':
        return week_or_month_flag
    else:
        logging.error('weekかmonthかyearを入力してください')
        sys.exit(1)

"""
実行時引数として以下の二つが必要
・全記事取得か月ごと、週間ごとに取得か(1 or 0)
・月ごとか週間ごとか年ごとのグラフを取得(month or week or year)
"""
if __name__ == '__main__':
    all_get_flag = check_digit_argv(sys.argv[1])
    week_or_month_flag = check_str_argv(sys.argv[2])
    main(all_get_flag, week_or_month_flag)