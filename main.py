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


class DataSet:
    def __init__(self):
        self.filepath = './record.json'
        if not os.path.exists(self.filepath):
            with open(self.filepath, 'w') as f:
                f.write('{"url": []}')

    def parse(self) -> dict:
        data = open(self.filepath, 'r').read()
        try:
            return json.loads(data)
        except JSONDecodeError:
            logger.fatal('資料結構錯誤。')

    def find(self, url: str) -> bool:
        data = self.parse()
        if data and 'url' in data.keys():
            if url in data['url']:
                return True
            return False
        return False

    def insert(self, url: str) -> bool:
        data = self.parse()
        if not data:
            logger.fatal('資料結構爛掉')
            return False
        if 'url' in data.keys():
            values = data['url']
            values.insert(0, url)
            data['url'] = values[:100]
        else:
            data['url'] = [url]
        # write
        t_ = json.dumps(data, ensure_ascii=False)
        with open(self.filepath, 'w') as f:
            f.write(t_)


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
    check = DataSet()
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
            check.insert(content.link)


def run():
    resource = fetch()
    if resource:
        data = parser(resource)
        broadcast(data)

while True:
    run()
    sleep(300)
