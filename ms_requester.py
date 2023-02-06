import asyncio
import math
import aiohttp
import json
from config import load_config, logger

config = load_config(".env")
token = config.g_conf.ms_token


recht_stock = {
    'meta': {
        'href': 'https://online.moysklad.ru/api/remap/1.2/entity/store/fdcec3ea-90c3-11ed-0a80-070b0009f546',
        'metadataHref': 'https://online.moysklad.ru/api/remap/1.2/entity/store/metadata',
        'type': 'store',
        'mediaType': 'application/json',
        'uuidHref': 'https://online.moysklad.ru/app/#warehouse/edit?id=fdcec3ea-90c3-11ed-0a80-070b0009f546'
      }
}
office_stock = {
    'meta': {
        'href': 'https://online.moysklad.ru/api/remap/1.2/entity/store/d4f77c31-912d-11ed-0a80-0e1700025bbd',
        'metadataHref': 'https://online.moysklad.ru/api/remap/1.2/entity/store/metadata',
        'type': 'store',
        'mediaType': 'application/json',
        'uuidHref': 'https://online.moysklad.ru/app/#warehouse/edit?id=d4f77c31-912d-11ed-0a80-0e1700025bbd'
      }
}


async def get_stock():
    async with aiohttp.ClientSession(headers={'Authorization': token}) as session:
        async with session.get(f'https://online.moysklad.ru/api/remap/1.2/entity/store') as resp:
            response = await resp.read()
        data = json.loads(response)['rows']
        meta = {'meta': data}
    print(len(meta['meta']))
    # return json.dumps(meta)
    return meta


async def get_organization():
    async with aiohttp.ClientSession(headers={'Authorization': token}) as session:
        async with session.get(f'https://online.moysklad.ru/api/remap/1.2/entity/organization') as resp:
            response = await resp.read()
        data = json.loads(response)['rows'][0]['meta']
        meta = {'meta': data}
    # return json.dumps(meta)
    return meta


async def get_products():
    async with aiohttp.ClientSession(headers={'Authorization': token}) as session:
        async with session.get(f'https://online.moysklad.ru/api/remap/1.2/entity/product') as resp:
            response = await resp.read()
        size = json.loads(response)['meta']['size']
    pages = math.ceil(size / 1000)
    res_list = []
    for i in range(pages):
        offset = i * 1000
        async with aiohttp.ClientSession(headers={'Authorization': token}) as session:
            async with session.get(f'https://online.moysklad.ru/api/remap/1.2/entity/product?offset={offset}') as resp:
                response = await resp.read()
            data = json.loads(response)['rows']
        for item in data:
            item_art = item['article']
            item_id = item['id']
            res_tuple = (item_art, item_id)
            res_list.append(res_tuple)
    return (res_list, size)


async def get_office_current():
    async with aiohttp.ClientSession(headers={'Authorization': token}) as session:
        async with session.get(f'https://online.moysklad.ru/api/remap/1.2/report/stock/bystore') as resp:
            response = await resp.read()
        data = json.loads(response)['rows']
        office_list = []
        for item in data:
            item_id = item['meta']['href'].split('/')[-1].split('?')[0]
            for stock in item['stockByStore']:
                if stock['meta']['href'] == office_stock['meta']['href'] and stock['stock'] > 0:
                    res_tuple = (item_id, int(stock['stock']))
                    office_list.append(res_tuple)
        return office_list


async def get_current():
    products_tuple = await get_products()
    product_list = products_tuple[0]
    size = products_tuple[1]
    pages = math.ceil(size / 1000)
    office_list = []
    recht_list = []
    recht_item_list = []
    for i in range(pages):
        offset = i * 1000
        async with aiohttp.ClientSession(headers={'Authorization': token}) as session:
            async with session.get(f'https://online.moysklad.ru/api/remap/1.2/report/stock/bystore?offset={offset}') as resp:
                response = await resp.read()
        data = json.loads(response)['rows']
        for item in data:
            item_id = item['meta']['href'].split('/')[-1].split('?')[0]
            for stock in item['stockByStore']:
                if stock['meta']['href'] == office_stock['meta']['href'] and stock['stock'] > 0:
                    for prod in product_list:
                        if item_id == prod[1]:
                            item_art = prod[0]
                            break
                    res_dict = {
                        'item_id': item_id,
                        'item_art': item_art,
                        'stock': int(stock['stock']),
                        'reserve': int(stock['reserve'])
                    }
                    office_list.append(res_dict)
                if stock['meta']['href'] == recht_stock['meta']['href']:
                    for prod in product_list:
                        if item_id == prod[1]:
                            item_art = prod[0]
                            break
                    res_dict = {
                        'item_id': item_id,
                        'item_art': item_art,
                        'stock': int(stock['stock']),
                        'reserve': int(stock['reserve'])
                    }
                    recht_item_list.append(item_id)
                    recht_list.append(res_dict)
    for prod in product_list:
        if prod[1] not in recht_item_list:
            item_art = prod[0]
            res_dict = {'item_id': prod[1], 'item_art': item_art, 'stock': 0, 'reserve': 0}
            recht_list.append(res_dict)
    result = {'office': office_list, 'recht': recht_list}
    return result


async def create_enter(enter_list):
    organization_meta = await get_organization()
    positions_list = []
    for item in enter_list:
        item_dict = {
            "quantity": item[1],
            "price": item[2],
            "assortment": {
                "meta": {
                    "href": f"https://online.moysklad.ru/api/remap/1.2/entity/product/{item[0]}",
                    "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/product/metadata",
                    "type": "product",
                    "mediaType": "application/json"
                }
            }
        }
        positions_list.append(item_dict)
    r_data = {
        'organization': organization_meta,
        'store': recht_stock,
        'positions': positions_list
    }
    req_data = json.dumps(r_data)
    async with aiohttp.ClientSession(headers={'Authorization': token, 'Content-Type': 'application/json'}) as session:
        await session.post(f'https://online.moysklad.ru/api/remap/1.2/entity/enter', data=req_data)
        logger.info(f'Оприходованно {len(enter_list)} позиций')


async def create_loss(loss_list):
    organization_meta = await get_organization()
    positions_list = []
    for item in loss_list:
        item_dict = {
            "quantity": item[1],
            "assortment": {
                "meta": {
                    "href": f"https://online.moysklad.ru/api/remap/1.2/entity/product/{item[0]}",
                    "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/product/metadata",
                    "type": "product",
                    "mediaType": "application/json"
                }
            }
        }
        positions_list.append(item_dict)
    r_data = {
        'organization': organization_meta,
        'store': recht_stock,
        'positions': positions_list
    }
    req_data = json.dumps(r_data)
    async with aiohttp.ClientSession(headers={'Authorization': token, 'Content-Type': 'application/json'}) as session:
        await session.post(f'https://online.moysklad.ru/api/remap/1.2/entity/loss', data=req_data)
        logger.info(f'Списано {len(loss_list)} позиций')

