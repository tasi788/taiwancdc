import requests
import feedparser
import logging
from typing import Union, List
from html2text import html2text
import json
from json.decoder import JSONDecodeError
import os
from html import escape
from time import sleep


logger = logging.getLogger(__name__)

class DataBase:
    def __init__(self):
        self.file = self.file_check()

    def file_check(self):
        if not os.path.exists('./record.json'):
            with open('./record.json', 'w', encoding='utf8') as f:
                f.write('{"id": []}')
        f = open('./record.json', 'r', encoding='utf8').read()
        return f

    def parse(self) -> dict:
        try:
            data = json.loads(self.file)
        except JSONDecodeError:
            logger.fatal('record.json 解析錯誤。')
        else:
            return data

    def find(self, id_: str) -> bool:
        data = self.parse()
        if id_ in data['id']:
            return True
        return False

    def add(self, id_: str) -> bool:
        data = self.parse()
        data['id'].append(id_)
        data['id'] = data['id'][:31]
        with open('./record.json', 'w', encoding='utf8') as f:
            f.write(
                json.dumps(data, ensure_ascii=False)
            )
        return True


def fetch() -> Union[str, bool]:
    url = 'https://www.cdc.gov.tw/RSS/RssXml/Hh094B49-DRwe2RR4eFfrQ?type=1'
    r = requests.get(url)
    if r.status_code == 200:
        return r.text
    logger.error(f'{r.status_code} - fetch rss resource error.')
    return False


def parser(content: str) -> list:
    rss = feedparser.parse(content)
    # text = html2text(rss.entries)
    return rss.entries


def broadcast(entries: List[feedparser.util.FeedParserDict]) -> bool:
    api_token = ''
    api_base = f'https://api.telegram.org/bot{api_token}/'
    # -1001224810715
    check = DataBase()
    for content in entries:
        if check.find(content.link):
            continue
        else:
            text = f'**{escape(content.title)}**\n' + \
                   html2text(content.summary)
            keyboard = {'inline_keyboard': [[{'text': '🔗 前往網頁', 'url': content.link}]]}
            payload = {'chat_id': -1001224810715, 'text': text, 'reply_markup': keyboard, 'parse_mode': 'markdown'}
            r = requests.post(
                api_base+'sendMessage',
                json=payload
            )
            check.add(content.link)


def run():
    resource = fetch()
    if resource:
        data = parser(resource)
        broadcast(data)

while True:
    run()
    sleep(300)
