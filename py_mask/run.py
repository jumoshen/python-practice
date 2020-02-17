import requests
import json
import time
import os
import pygame
from threading import Thread
import datetime


def run(link, t_id):
    while True:
        page_data = requests.post(link, data={"topic_id": t_id, "page": 1}, )
        init_data = json.loads(page_data.text)

        current = init_data['list'][0]
        current_origin_id = current['origin_id']
        history_id = int(get_origin_id())

        print(datetime.datetime.now())
        print(init_data['list'][0])
        print("\r\n")

        if current_origin_id > history_id:
            goods_url = current['url']
            os.system("/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome " + goods_url)
            Thread(target=speak())
            set_origin_id(current_origin_id)

        time.sleep(0.1)


def get_origin_id():
    with open('./origin_id.txt', 'r') as f:
        return f.read()


def set_origin_id(origin_id):
    with open('./origin_id.txt', 'w') as f:
        return f.write(str(origin_id))


def speak(duration=5):
    file = r'./gaobaiqiqiu.mp3'
    pygame.mixer.init()
    pygame.mixer.music.load(file)

    pygame.mixer.music.play()
    time.sleep(duration)
    pygame.mixer.music.stop()


if __name__ == '__main__':
    url = 'http://kz.sync163.com/api/topic/cards'
    topic_id = '37MRG2dObJQjv'
    # topic_id = 'XbBg4VqLnR7Z5'
    # topic_id = 'XbBg4VqLnR7Z5'
    run(url, topic_id)
