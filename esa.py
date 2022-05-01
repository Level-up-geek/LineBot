from dotenv import load_dotenv
load_dotenv()
from pandas.core.common import flatten

import requests, datetime, datetime, os, logging, sys, calendar

"""
週間ごと、月ごと記事情報の取得を行う。
"""
def get_posts(query_date, team_name, week_or_month_flag):
    access_token = os.getenv('ESA_ACCESS_TOKEN')
    if week_or_month_flag == 'week':
        query_date_str = [date.strftime('%Y-%m-%d') for date in query_date]
        #esaのqueryでは~以下ができない。未満しかできないので週の最終日を+1して置き換える取得する。
        query_date_last = str(int(query_date_str[-1].split('-')[2]) + 1).zfill(2)
        week_last_date = query_date_str[-1][:8] + query_date_last
        q = f'created: <{week_last_date} created: >{query_date_str[0]}'
    else:
        #monthの場合は既にquery_dateがstr型
        q = f'created: <{query_date[1]} created: >{query_date[0]}'
    
    url = f'https://api.esa.io/v1/teams/{team_name}/posts'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json;charset=UTF-8'
    }

    next_page = 0
    pre_month = '0'
    pre_year = '0'
    result = {}

    while next_page is not None:
        body = {
            'page': next_page,
            'q': q,
            'sort': 'created'
        }
        res = requests.get(url, headers=headers, params=body)
        #MEMO:本当はここからは、get_postsとは関係ないので他の関数でやった方がいい
        if res.status_code == 200:
            next_page = res.json()['next_page']
            
            if next_page is None:
                logging.info('残りリクエスト数: ' + res.headers['X-RateLimit-Remaining'])
                logging.info('リセット時間: ' + str(datetime.datetime.fromtimestamp(int((res.headers['X-RateLimit-Reset'])))))

            result, pre_month, pre_year  = create_posts_per_date(res, posts_per_date=result, pre_month=pre_month, pre_year=pre_year)
        else:
            logging.error(res.json())
            sys.exit(1)
    
    if pre_month == '0':
        logging.error('投稿していない月または週があります。正しいデータを作成できません')
        sys.exit(1)
    
    if week_or_month_flag == 'week':
        return extract_week_list(result, pre_month, pre_year, query_date)
    else:
        return result

""""
すべての記事情報の取得
ローカルで最初に実行するものかな
"""
def get_all_posts(team_name):
    access_token = os.getenv('ESA_ACCESS_TOKEN')

    url = f'https://api.esa.io/v1/teams/{team_name}/posts'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json;charset=UTF-8'
    }
    
    next_page = 0
    result = {}
    pre_month = '0'
    pre_year = '0'
    
    while next_page is not None:
        body = {
            'sort': 'created',
            'page': next_page
        }

        res = requests.get(url, headers=headers, params=body)

        if res.status_code == 200:
            next_page = res.json()['next_page']

            if next_page is None:
                logging.info('残りリクエスト数: ' + res.headers['X-RateLimit-Remaining'])
                logging.info('リセット時間: ' + str(datetime.datetime.fromtimestamp(int((res.headers['X-RateLimit-Reset'])))))
            
            result, pre_month, pre_year = create_posts_per_date(res, posts_per_date=result, pre_month=pre_month, pre_year=pre_year)
        else:
            logging.error(res.json())
    
    if pre_month == '0':
        logging.error('今月は投稿されていないです。正しいデータを作成できません')
        sys.exit(1)

    return result

"""
メンバーの名前を取得しておく
spreadsheetでメンバーごとにシート作る
"""
def get_members(team_name):
    access_token = os.getenv('ESA_ACCESS_TOKEN')

    url = f'https://api.esa.io/v1/teams/{team_name}/members'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json;charset=UTF-8'
    }
    res = requests.get(url, headers=headers)
    
    return [member['screen_name'] for member in res.json()['members'] if member != 'esa_bot']

""""
ユーザごとの日付ごとに投稿した数

投稿データを取得してその投稿日から、
その年、月や日にちの初期化であったり、投稿数のカウントをしている
"""
def create_posts_per_date(res, posts_per_date={}, pre_month=0, pre_year=0):
    #MEMO:最初の一回だけでいいよね。
    members = get_members('level-up-geek')

    for person in members:
        if not person in posts_per_date:
            posts_per_date[person] = {}

    for post in res.json()['posts']:
        date = datetime.datetime.fromisoformat(post['created_at']).date()
        year = str(date.year)
        month = str(date.month)
        day = str(date.day)
        member = post['created_by']['screen_name']
        
        if member ==  'esa_bot':
            continue
        else: 
            #投稿ごとにposts_per_dateのmonthとを比較して異なればその異なる月の日にちごとの投稿数を初期化する
            if year != pre_year:
                pre_year = year
                for person in members:
                    posts_per_date[person][year] = {}

            if month != pre_month:
                pre_month = month

                #月の日にちをすべて取得する
                original_day_list = calendar.monthcalendar(year=int(year), month=int(month))
                #特定の要素すべて削除
                day_list = [day for day in list(flatten(original_day_list)) if day != 0]

                for person in members:    
                    posts_per_date[person][year][month] = {}
                    for d in day_list:
                        posts_per_date[person][year][month][str(d)] = 0
            
            posts_per_date[member][year][month][day] += 1
    #このページでの最後の投稿の月を返す
    return posts_per_date, pre_month, pre_year

"""
post_per_dateから抽出したい週のdictを返す
query_date: 抽出したい週(date型)の日付けが入ったのリスト

・注意
query_dateで月をまたいでいる場合、次の月の投稿がされてないとkeyエラーになる
(普通は、cronでスケジュールされてるからまだ投稿されていない月が含まれる形で実行はされないはず。)
"""
def extract_week_list(post_per_date_user, month, year, query_date):
    other_month = None

    c = calendar.monthcalendar(year=int(year), month=int(month) + 1)
    next_day_list = [day for day in list(flatten(c)) if day != 0]

    c = calendar.monthcalendar(year=int(year), month=int(month) - 1)
    pre_day_list = [day for day in list(flatten(c)) if day != 0]
    #月をまたがった時の対応
    if datetime.date(int(year), int(month) - 1, pre_day_list[-1]) in query_date:
        other_month = str(int(month) - 1)
    elif datetime.date(int(year), int(month) + 1, next_day_list[0]) in query_date:
        other_month = str(int(month) + 1)
    #MEMO:1月の時の対応(年マタギ)
    #[year]も月の時のように処理しないといけない。

    for user, post_per_date in post_per_date_user.items():
        for day in list(post_per_date[year][month].keys()):
            if datetime.date(int(year), int(month), int(day)) not in query_date:
                post_per_date_user[user][year][month].pop(day)
        if other_month is not None:
            for day in list(post_per_date[year][other_month].keys()):
                if datetime.date(int(year), int(other_month), int(day)) not in query_date:
                    post_per_date_user[user][year][other_month].pop(day)
    
    return post_per_date_user