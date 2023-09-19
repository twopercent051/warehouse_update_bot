import asyncio
import json
from typing import Literal

from bs4 import BeautifulSoup
import aiohttp
from config import load_config

config = load_config(".env")


class ShopParser:

    def __init__(self):
        self.recht_login = config.g_conf.recht_login
        self.recht_psw = config.g_conf.recht_psw
        self.unas_url = config.g_conf.unas_url

    async def __get_recht_info(self, item_art):
        try:
            url = f'https://www.oreht.ru/modules.php?name=orehtPriceLS&op=ShowInfo&code={item_art}'
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'referer': url
            }
            data = {'inn': self.recht_login, 'pass': self.recht_psw}
            async with aiohttp.ClientSession() as session:
                async with session.post(url=url, headers=headers, data=data) as resp:
                    src = await resp.text()
            soup = BeautifulSoup(src, 'lxml')
            stock_balance = soup.find(class_='mg-is-k').text
            try:
                price = soup.find(class_='mg-price').text.replace(',', '.').replace('\n', '')
                price = float(price)
            except (TypeError, ValueError):
                price = None
            return dict(quantity=int(stock_balance), price=int(price * 100))
        except:
            return

    async def __get_unas_info(self, item_art):
        async with aiohttp.ClientSession() as session:
            async with session.get(url=f"{self.unas_url}/{item_art}") as resp:
                response = await resp.read()
            if response:
                data = json.loads(response)
                return dict(quantity=int(data["quantity"]), price=int(data["cost"]))

    async def get_shop_data(self, shop_title: Literal["recht", "unas"], item_art: str):
        item_art = item_art.split("-")[-1]
        if shop_title == "recht":
            data = await self.__get_recht_info(item_art=item_art)
        else:
            data = await self.__get_unas_info(item_art=item_art)
        return data


async def main():
    a = ShopParser()
    res = await a.get_shop_data(shop_title="unas", item_art="qwer-00031595")
    print(res)

if __name__ == "__main__":
    asyncio.run(main())

