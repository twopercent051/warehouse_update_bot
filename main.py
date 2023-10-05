import time
from datetime import datetime
from typing import List, Literal

from ms_requester import MSApi
from shop_parser import ShopParser
import asyncio
from config import logger
from telegram import message

ms_api = MSApi()
shop_data = ShopParser()


class Main:

    @staticmethod
    async def __dispatch_item(office_items: List[dict], stock_items: List[dict], stock_type: Literal["recht", "unas"]):
        enter_list = []
        loss_list = []
        count = 0
        office_list = [i["item_id"] for i in office_items]
        for item in stock_items:
            count += 1
            for office_item in office_items:
                if item['item_id'] in office_item['item_id']:
                    diff = item['stock']
                    if diff > 0:
                        logger.info(f'Ненулевой офис. Списание {diff} шт || Артикул {item["item_art"]}')
                        await message(f'Ненулевой офис. Списание {diff} шт || Артикул {item["item_art"]}')
                        res_tuple = (item['item_id'], diff)
                        loss_list.append(res_tuple)
            if item['item_id'] not in office_list:
                shop_res = await shop_data.get_shop_data(shop_title=stock_type, item_art=item["item_art"])
                if shop_res:
                    price = shop_res["price"]
                    balance = shop_res["quantity"] - 1 if shop_res["quantity"] > 0 else 0
                    if item['stock'] == balance:
                        pass
                    if item['stock'] < balance:
                        diff = balance - item['stock']
                        res_tuple = (item['item_id'], diff, price)
                        logger.info(f'Расхождение склада. Оприходование {diff} шт || Артикул {item["item_art"]}')
                        await message(f'Расхождение склада. Оприходование {diff} шт || Артикул {item["item_art"]}')
                        enter_list.append(res_tuple)
                    if item['stock'] > balance:
                        diff = item['stock'] - balance
                        res_tuple = (item['item_id'], diff)
                        logger.info(f'Расхождение склада. Списание {diff} шт || Артикул {item["item_art"]}')
                        await message(f'Расхождение склада. Списание {diff} шт || Артикул {item["item_art"]}')
                        loss_list.append(res_tuple)
                else:
                    diff = item['stock']
                    if diff > 0:
                        logger.info(f'Битая ссылка. Списание {diff} шт || Артикул {item["item_art"]}')
                        await message(f'Битая ссылка. Списание {diff} шт || Артикул {item["item_art"]}')
                        res_tuple = (item['item_id'], diff)
                        loss_list.append(res_tuple)
            # if count % 100 == 0 or count == len(stock_items):
            if len(enter_list) == 10 or count == len(stock_items):
                await ms_api.stock_operation(type_operation="enter", stock_type=stock_type, item_list=enter_list)
            if len(loss_list) == 10 or count == len(stock_items):
                await ms_api.stock_operation(type_operation="loss", stock_type=stock_type, item_list=loss_list)
            loss_list = []
            enter_list = []

    @classmethod
    async def main(cls):
        stock = await ms_api.get_current()
        logger.info(f'NEW WHILE')
        await message(f"Начало цикла. В списке {len(stock['recht'])} позиций")
        await cls.__dispatch_item(office_items=stock["office"], stock_items=stock["recht"], stock_type="recht")
        await cls.__dispatch_item(office_items=stock["office"], stock_items=stock["unas"], stock_type="unas")
        logger.info('DONE')
        time.sleep(2)


if __name__ == '__main__':
    while True:
        asyncio.run(Main.main())
        # try:
        #     asyncio.run(Main.main())
        # except Exception as ex:
        #     time.sleep(15)
        #     logger.info(f"Running again after {ex}!")
