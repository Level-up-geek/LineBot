from dotenv import load_dotenv
load_dotenv()

import requests, json, datetime, os, logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def main():
    result = get_all_posts('level-up-geek')
    print(result)
    return result
    #result = get_posts('2022/03/14', 'level-up-geek')
    #print(result)


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
    
    return create_posts_per_date(res)

   
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
    alt_result = {}
    result = {}
    members = []
    
    while next_page is not None:
        body = {
            'sort': 'created',
            'page': next_page
        }

        res = requests.get(url, headers=headers, params=body)
        #print(json.dumps(res.json(), indent=2))
        if res.status_code == 200:
            next_page = res.json()['next_page']

            if next_page is None:
                logging.info('残りリクエスト数: ' + res.headers['X-RateLimit-Remaining'])
                logging.info('リセット時間: ' + str(datetime.datetime.fromtimestamp(int((res.headers['X-RateLimit-Reset'])))))
            
            alt_result, members = create_posts_per_date(res)

            for member in members:
                if not member in result:
                    result[member] = {}

                result[member] |= alt_result[member]

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
def create_posts_per_date(res):
    posts_per_date = {}
    members = get_members('level-up-geek')

    for member in members:
        posts_per_date[member] = {}

    for post in res.json()['posts']:
        date = datetime.datetime.fromisoformat(post['created_at']).strftime('%Y-%m-%d')
        member = post['created_by']['screen_name']
        if member ==  'esa_bot':
            continue
        else: 
            #MEMO:日付は非連続ー＞1週間のグラフ化の時date in hash->falseならhash[date] = 0とする
            if date in posts_per_date[member]:
                posts_per_date[member][date] += 1
            else:
                posts_per_date[member][date] = 1

    return posts_per_date, members

if __name__ == '__main__':
    main()


