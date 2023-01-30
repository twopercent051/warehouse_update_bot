from bs4 import BeautifulSoup
import requests
import aiohttp
from datetime import datetime
from config import load_config, logger

config = load_config(".env")

recht_login = config.g_conf.recht_login
recht_psw = config.g_conf.recht_psw


def timeit(func):
    def wrapper(*args, **kwargs):
        start = datetime.now()
        result = func(*args, **kwargs)
        logger.info(datetime.now() - start)
        return result

    return wrapper


# @timeit
async def get_card_info(item_art):
    url = f'https://www.oreht.ru/modules.php?name=orehtPriceLS&op=ShowInfo&code={item_art}'
    headers = {'Content-Type': 'application/x-www-form-urlencoded',
               'referer': url
               }
    data = {'inn': recht_login, 'pass': recht_psw}
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, headers=headers, data=data) as resp:
            src = await resp.text()
    try:
        # url = f'https://www.oreht.ru/modules.php?name=orehtPriceLS&op=ShowInfo&code={item_art}'
        # session = requests.Session()
        # headers = {'Content-Type': 'application/x-www-form-urlencoded',
        #            'referer': url
        #            }
        # session.post(url, data={'inn': recht_login, 'pass': recht_psw}, headers=headers)
        # src = session.get(url).text
        soup = BeautifulSoup(src, 'lxml')
        stock_balance = soup.find(class_='mg-is-k').text
        print(stock_balance)
        try:
            price = soup.find(class_='mg-price').text.replace(',', '.').replace('\n', '')
            price = float(price)
        except:
            price = None
        return stock_balance, price
    except:
        return False
