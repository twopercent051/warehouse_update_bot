import time
from recht_parser import get_card_info
from ms_requester import get_current, create_enter, create_loss
import asyncio
from config import logger


async def main():
    stock = await get_current()
    logger.info(f'NEW WHILE || LEN: {len(stock["recht"])}')
    office_list = []
    enter_list = []
    loss_list = []
    count = 0
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
                logger.info(f'Ненулевой офис. Списание {diff} шт || Артикул {item["item_art"]}')
                res_tuple = (item['item_id'], diff)
                loss_list.append(res_tuple)
        if item['item_id'] not in office_list:
            art_num = item['item_art'].split('-')[-1]
            recht_res = get_card_info(art_num)
            price = recht_res[1] * 100
            if recht_res and recht_res[0].isdigit():
                balance = recht_res[0]
                balance = int(balance)
                logger.info(f'Баланс {balance} || Склад {item["stock"]} || Артикул {item["item_art"]}')
                if item['stock'] == balance:
                    pass
                if item['stock'] < balance:
                    diff = balance - item['stock']
                    res_tuple = (item['item_id'], diff, price)
                    enter_list.append(res_tuple)
                if item['stock'] > balance:
                    diff = item['stock'] - balance
                    res_tuple = (item['item_id'], diff)
                    loss_list.append(res_tuple)
        if count % 100 == 0 or count == len(stock['recht']):
            if len(enter_list) > 0:
                await create_enter(enter_list)
            if len(loss_list) > 0:
                await create_loss(loss_list)
            office_list = []
            enter_list = []
    logger.info('DONE')
    time.sleep(2)


if __name__ == '__main__':
    while True:
        try:
            asyncio.run(main())
        except Exception as ex:
            time.sleep(15)
            logger.info(f"Running again after {ex}!")
