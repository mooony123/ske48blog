from bs4 import BeautifulSoup
from datetime import datetime
import os
import pprint
import re
import requests
import pytz
import json
import asyncio
import aiohttp

tz = pytz.timezone('Japan')
BASE_URL='https://ske48.co.jp'

TITLE = 'title'
AUTHOR = 'author'
DATE = 'date'
TEXT = 'text'
IMAGES = 'images'

JSON_FILE_NAME = 'ske48blog.json'
latest_blogs = {}


def parse_blog(url: str) -> dict:
    return_dict = {TITLE: '', AUTHOR: '', DATE: '', TEXT: '', IMAGES: []}

    page = requests.get(url)
    if page.status_code != requests.codes.ok:
        return {}
    soup = BeautifulSoup(page.content, 'html.parser')

    blog_section = soup.find('section', class_='section--detail')

    return_dict[TITLE] = blog_section.find('p', class_='tit').get_text()
    return_dict[AUTHOR] = blog_section.find('span', class_='cat name').get_text()
    return_dict[DATE] = blog_section.find('p', class_='date').get_text()
    for para in blog_section.find('div', class_='txt').find_all('p'):
        return_dict[TEXT] += (para.get_text() + '\n')
    for img in blog_section.find('div', class_='txt').find_all('img'):
        return_dict[IMAGES].append(img['src'])

    return return_dict

def blog_to_str(blog: dict) -> str:
    return_str = f'{blog[TITLE]}\n' \
                 f'{blog[AUTHOR]} {blog[DATE]}\n'\
                 f'{blog[TEXT]}'
    return return_str

async def get_new_blogs() -> list:
    retval = []

    page = requests.get('https://ske48.co.jp/blog/list/3/0/')
    soup = BeautifulSoup(page.content, 'html.parser')

    async def get(name, aiohttpsession):
        if name.get_text() == 'ALL':
            return (0, None)
        ident = name['value'].split('/')[-2]
        async with aiohttpsession.get(url=(BASE_URL+name['value'])) as resp:
            ipage = await resp.text()
        return (ident, ipage)
    async with aiohttp.ClientSession() as session:
        responses = await asyncio.gather(*[get(name, session) for
                                         name in soup.find('select').find_all('option')])
    for ident, ipage in responses:
        if ident == 0:
            continue
        isoup = BeautifulSoup(ipage, 'html.parser')
        first = isoup.find('a', class_='clearfix')
        if first == None:
            continue
        url = BASE_URL+first['href']
        if ident not in latest_blogs or latest_blogs[ident] != url:
            latest_blogs[ident] = url
            retval.append(latest_blogs[ident])
    if len(retval):
        with open(JSON_FILE_NAME, 'w') as f:
            json.dump(latest_blogs, f)

    return retval

async def init():
    global latest_blogs
    if os.path.isfile(JSON_FILE_NAME):
        with open(JSON_FILE_NAME, 'r') as f:
            latest_blogs = json.load(f)
    else:
        await get_new_blogs()

async def main():
    await init()
    new_blogs = await get_new_blogs()
    if not len(new_blogs):
        new_blogs.append(latest_blogs[next(iter(latest_blogs))])
    for url in new_blogs:
        blog_dict = parse_blog(url)
        print(blog_to_str(blog_dict))

if __name__ == '__main__':
    asyncio.run(main())

