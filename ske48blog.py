from bs4 import BeautifulSoup
from datetime import datetime
import pprint
import re
import requests
import pytz

tz = pytz.timezone('Japan')
BASE_URL='https://ske48.co.jp'

TITLE = 'title'
AUTHOR = 'author'
DATE = 'date'
TEXT = 'text'
IMAGES = 'images'

import pprint

def parse_blog(url: str) -> dict:
    return_dict = {TEXT: '', IMAGES: []}

    page = requests.get(url)
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

if __name__ == '__main__':
    blog_dict = parse_blog('https://ske48.co.jp/blog/detail/77510/')
    pprint.pprint(blog_dict)
    pass
