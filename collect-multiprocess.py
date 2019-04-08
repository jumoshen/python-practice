#!/usr/local/bin/python3
import requests
from fake_useragent import UserAgent
import json
from peewee import *
import datetime
import time
from multiprocessing import Process, Pool
import os
import logging
import traceback

logging.basicConfig(level=logging.ERROR,
                    filename='collect-multiprocess.log',
                    filemode='a',
                    format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
                    )

id_all = {"动作": 1, "角色扮演": 5, "横版过关": 41, "冒险": 4, "射击": 48, "第一人称射击": 32,
          "策略": 2, "益智": 18, "模拟": 7, "体育": 3, "竞速": 6, "格斗": 9, "乱斗/清版": 37, "即时战略": 12, "音乐/旋律": 19}

comment_api = 'https://www.douban.com/j/ilmen/game/search?genres={}&platforms=&q=&sort=rating&more={}'

db = MySQLDatabase('thinkphp', user='root', charset='utf8mb4')


class DouBanGame(Model):
    title = CharField()
    cover = CharField()
    star = CharField()
    type = CharField()
    rating = CharField()
    platforms = CharField()
    n_ratings = CharField()
    genres = CharField()
    content = CharField()
    create_at = DateTimeField()

    class Meta:
        database = db
        table_name = 'douban_games'


def get_data(genres):
    # print('Run task as %s (%s)...' % (genres, os.getpid()))

    id_all_reverse = dict([val, key] for key, val in id_all.items())

    link = comment_api.format(genres, 1)

    headers = {"User-Agent": UserAgent(verify_ssl=False).random}

    page_data = requests.get(link, headers=headers)

    init_data = json.loads(page_data.text)

    col = ['name', 'star', 'rating', 'platforms', 'n_ratings', 'genres', 'content']

    total = init_data['total']
    print('{}类别共{}个游戏,开始爬取!'.format(id_all_reverse[genres], total))

    i = 0
    while i < total:
        data = []
        game_type = id_all_reverse[genres]

        if i == 0:
            n = 1
        else:
            n = init_data['more']

        init_data = json.loads(requests.get(comment_api.format(genres, n), headers=headers).text)

        current_games = init_data['games']

        length = len(init_data['games'])

        for j in range(length - 1):
            data.append({
                'title': current_games[j]['title'],
                'cover': current_games[j]['cover'],
                'type': game_type,
                'star': current_games[j]['star'],
                'rating': current_games[j]['rating'],
                'platforms': current_games[j]['platforms'],
                'n_ratings': current_games[j]['n_ratings'],
                'genres': current_games[j]['genres'],
                'content': (current_games[j]['review']['content'] if isinstance(current_games[j]['review']['content'],
                                                                                str) else ''),
                'create_at': datetime.datetime.now()
            })
            i += 1
        # time.sleep(0.8)

        if data:
            print(data)
            last_id = DouBanGame.insert_many(data).execute()
            print(last_id)
        else:
            print('empty data!')
            print('NO%s' % i)
            break


if __name__ == '__main__':
    comment_api = 'https://www.douban.com/j/ilmen/game/search?genres={}&platforms=&q=&sort=rating&more={}'

    print('Parent process %s.' % os.getpid())

    try:

        p = Pool(4)

        for genres in list(id_all.values()):
            p.apply_async(get_data, args=(genres,))

        print("waiting for all subProcesses done...")
        p.close()
        p.join()
        print('All subProcesses done.')
    except Exception as e:
        logging.info(traceback.format_exc())

