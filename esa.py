from dotenv import load_dotenv
load_dotenv()

import requests, datetime, datetime, os, logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def get_posts(query_date, team_name):
    url = f'https://api.esa.io/v1/teams/{team_name}/posts'
    headers = {
        'Authorization': 'Bearer {}'.format('cHloQoCpA3NELDRvHDMw8KqqBd1UuxO7E8okDobtFwk'),
        'Content-Type': 'application/json;charset=UTF-8'
    }
    body = {
        'q': f'created:{query_date}',
        'sort': 'created'
    }
    res = requests.get(url, headers=headers, params=body)
    
    #post_per_date, month, year
    alt_result = create_posts_per_date(res, every_day_flag=True)
    
    #当日の分だけ抽出するための情報を定義
    year = alt_result[2]
    month = alt_result[1]
    day = query_date.split('-')[2]

    result = {}

    for user, post_per_date in alt_result[0].items():
        result |= {user: {year: {month: {date: posts_count}}}  for date, posts_count in post_per_date[year][month].items() if date == day}
    
    return result

   
""""
これは最初の一回だけ実行される
以降はget_postsで毎日一回実行され
postsの差分をgetしていく
"""
def get_all_posts(team_name):
    url = f'https://api.esa.io/v1/teams/{team_name}/posts'
    headers = {
        'Authorization': 'Bearer {}'.format('cHloQoCpA3NELDRvHDMw8KqqBd1UuxO7E8okDobtFwk'),
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

"""
def create_posts_per_date(res, every_day_flag=False, posts_per_date={}, pre_month=0, pre_year=0):
    #MEMO:最初の一回だけでいいよね。
    members = get_members('level-up-geek')
    
    for member in members:
        if not member in posts_per_date:
            posts_per_date[member] = {}

    for post in res.json()['posts']:
        date = datetime.datetime.fromisoformat(post['created_at']).date()
        year = str(date.year)
        month = str(date.month)
        day = str(date.day)
        
        if post['created_by']['screen_name'] ==  'esa_bot':
            continue
        else: 
            #投稿ごとにposts_per_dateのmonthとを比較して異なればその異なる月の日にちごとの投稿数を初期化する
            if year != pre_year:
                pre_year = year
                for member in members:
                    posts_per_date[member][year] = {}

            if month != pre_month:
                pre_month = month

                from pandas.core.common import flatten
                import calendar
                #月の日にちをすべて取得する
                original_day_list = calendar.monthcalendar(year=int(year), month=int(month))
                #特定の要素すべて削除
                day_list = [day for day in list(flatten(original_day_list)) if day != 0]

                for member in members:    
                    posts_per_date[member][year][month] = {}
                    for d in day_list:
                        posts_per_date[member][year][month][str(d)] = 0
            
            posts_per_date[member][year][month][day] += 1
    
    #このページでの最後の投稿の月を返す
    return posts_per_date, month, year
