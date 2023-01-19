import asyncio
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import lxml
import aiohttp
import json
from config import load_config

config = load_config(".env")

recht_login = config.g_conf.recht_login
recht_psw = config.g_conf.recht_psw

def get_office_current():
    url = 'https://www.oreht.ru/modules.php?name=orehtPriceLS&op=ShowInfo&code=387059'
    session = requests.Session()
    headers = {'Content-Type': 'application/x-www-form-urlencoded',
               'referer': url
               }
    session.post(url, data={'inn': recht_login, 'pass': recht_psw}, headers=headers)
    src = session.get(url).text
    soup = BeautifulSoup(src, 'lxml')

    name = soup.find(class_='mg-h1text').text
    stock = soup.find(class_='mg-is-k').text
    print(name)
    print(stock)


get_office_current()




