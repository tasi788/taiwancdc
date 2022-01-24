import requests
import feedparser
import logging
from typing import Union, List
from html2text import html2text
from html import escape
from time import sleep
from tinydb import TinyDB, Query

logger = logging.getLogger(__name__)
db = TinyDB('db.json')


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

    for content in entries:
        rss_query = Query()
        result = db.search(rss_query.link == content.link)
        if result:
            continue
        else:
            text = f'**{escape(content.title)}**\n' + \
                   html2text(content.summary)
            keyboard = {'inline_keyboard': [[{'text': '🔗 前往網頁', 'url': content.link}]]}
            payload = {'chat_id': -1001224810715, 'text': text, 'reply_markup': keyboard, 'parse_mode': 'markdown'}
            r = requests.post(
                api_base + 'sendMessage',
                json=payload
            )
            db.insert({'link': content.link})
            extrator = db.all()
            for r in extrator[20:]:
                rss_query = Query()
                db.remove(rss_query.link == r['link'])


def run():
    resource = fetch()
    if resource:
        data = parser(resource)
        broadcast(data)


def first_run():
    resource = fetch()
    if resource:
        for data in parser(resource):
            db.insert({'link': data.link})


first_run()

while True:
    run()
    sleep(300)
