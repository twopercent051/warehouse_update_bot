import time
from recht_parser import get_card_info
from ms_requester import get_current, create_enter, create_loss
import asyncio
from config import logger
from telegram import message


async def main():
    stock = await get_current()
    logger.info(f'NEW WHILE || LEN: {len(stock["recht"])}')
    await message(f"Начало цикла. В списке {len(stock['recht'])} позиций")
    office_list = []
    enter_list = []
    loss_list = []
    count = 0
    st = time.time()
    for office_item in stock['office']:
        if office_item['stock'] != 0:
            office_list.append(office_item['item_id'])
    for item in stock['recht']:
        count += 1
        logger.info(f'Item # {count}')
        if item['item_art'][:4] != 'РСВ-':
            continue
        for office_item in stock['office']:
            if item['item_id'] in office_item['item_id']:
                diff = item['stock']
                if diff > 0:
                    logger.info(f'Ненулевой офис. Списание {diff} шт || Артикул {item["item_art"]}')
                    await message(f'Ненулевой офис. Списание {diff} шт || Артикул {item["item_art"]}')
                    res_tuple = (item['item_id'], diff)
                    loss_list.append(res_tuple)
        if item['item_id'] not in office_list:
            art_num = item['item_art'].split('-')[-1]
            recht_res = await get_card_info(art_num)
            if recht_res and recht_res[0].isdigit():
                price = recht_res[1] * 100
                balance = recht_res[0]
                balance = int(balance)
                # logger.info(f'Баланс {balance} || Склад {item["stock"]} || Артикул {item["item_art"]}')
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
        if count % 100 == 0 or count == len(stock['recht']):
            if len(enter_list) > 0:
                await create_enter(enter_list)
            if len(loss_list) > 0:
                await create_loss(loss_list)
            loss_list = []
            enter_list = []
            ft = time.time()
            logger.info(ft - st)
    logger.info('DONE')
    time.sleep(2)


if __name__ == '__main__':
    while True:
        try:
            asyncio.run(main())
        except Exception as ex:
            time.sleep(15)
            logger.info(f"Running again after {ex}!")
