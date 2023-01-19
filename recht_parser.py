from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import requests
import time
from datetime import datetime
from config import load_config

config = load_config(".env")

recht_login = config.g_conf.recht_login
recht_psw = config.g_conf.recht_psw


def timeit(func):
    def wrapper(*args, **kwargs):
        start = datetime.now()
        result = func(*args, **kwargs)
        print(datetime.now() - start)
        return result
    return wrapper


@timeit
def get_card_info(item_art):
    try:
        url = f'https://www.oreht.ru/modules.php?name=orehtPriceLS&op=ShowInfo&code={item_art}'
        session = requests.Session()
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                   'referer': url
                   }
        session.post(url, data={'inn': recht_login, 'pass': recht_psw}, headers=headers)
        src = session.get(url).text
        soup = BeautifulSoup(src, 'lxml')
        stock_balance = soup.find(class_='mg-is-k').text
        try:
            price = soup.find(class_='mg-price').text.replace(',', '.').replace('\n', '')
            price = float(price)
        except:
            price = None
        return (stock_balance, price)
    except:
        return False
