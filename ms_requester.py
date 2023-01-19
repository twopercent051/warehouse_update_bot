import aiohttp
import json
from config import load_config

config = load_config(".env")
token = config.g_conf.ms_token


main_stock = {
    'meta': {
      'href': 'https://online.moysklad.ru/api/remap/1.2/entity/store/7f5ea16d-9120-11ed-0a80-07110001c248',
      'metadataHref': 'https://online.moysklad.ru/api/remap/1.2/entity/store/metadata',
      'type': 'store',
      'mediaType': 'application/json',
      'uuidHref': 'https://online.moysklad.ru/app/#warehouse/edit?id=7f5ea16d-9120-11ed-0a80-07110001c248'
    }
}
recht_stock = {
    'meta': {
      'href': 'https://online.moysklad.ru/api/remap/1.2/entity/store/dc49930d-92ad-11ed-0a80-029c0002a214',
      'metadataHref': 'https://online.moysklad.ru/api/remap/1.2/entity/store/metadata',
      'type': 'store',
      'mediaType': 'application/json',
      'uuidHref': 'https://online.moysklad.ru/app/#warehouse/edit?id=dc49930d-92ad-11ed-0a80-029c0002a214'
    }
}
office_stock = {
    'meta': {
      'href': 'https://online.moysklad.ru/api/remap/1.2/entity/store/dc5d17b2-92ad-11ed-0a80-05c700029455',
      'metadataHref': 'https://online.moysklad.ru/api/remap/1.2/entity/store/metadata',
      'type': 'store',
      'mediaType': 'application/json',
      'uuidHref': 'https://online.moysklad.ru/app/#warehouse/edit?id=dc5d17b2-92ad-11ed-0a80-05c700029455'
    }
}


async def get_stock():
    async with aiohttp.ClientSession(headers={'Authorization': token}) as session:
        async with session.get(f'https://online.moysklad.ru/api/remap/1.2/entity/store') as resp:
            response = await resp.read()
        data = json.loads(response)['rows']
        meta = {'meta': data}
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
        data = json.loads(response)['rows']
    res_list = []
    for item in data:
        item_art = item['article']
        item_id = item['id']
        res_tuple = (item_art, item_id)
        res_list.append(res_tuple)
    return res_list


async def get_office_current():
    async with aiohttp.ClientSession(headers={'Authorization': token}) as session:
        async with session.get(f'https://online.moysklad.ru/api/remap/1.2/report/stock/bystore') as resp:
            response = await resp.read()
        data = json.loads(response)['rows']
        print(data)
        office_list = []
        for item in data:
            item_id = item['meta']['href'].split('/')[-1].split('?')[0]
            for stock in item['stockByStore']:
                if stock['meta']['href'] == office_stock['meta']['href'] and stock['stock'] > 0:
                    res_tuple = (item_id, int(stock['stock']))
                    office_list.append(res_tuple)
        print(office_list)
        return office_list


async def get_current():
    async with aiohttp.ClientSession(headers={'Authorization': token}) as session:
        async with session.get(f'https://online.moysklad.ru/api/remap/1.2/report/stock/bystore') as resp:
            response = await resp.read()
        data = json.loads(response)['rows']
        product_list = await get_products()
        office_list = []
        recht_list = []
        recht_item_list = []
        for item in data:
            item_id = item['meta']['href'].split('/')[-1].split('?')[0]
            for stock in item['stockByStore']:
                if stock['meta']['href'] == office_stock['meta']['href'] and stock['stock'] > 0:
                    # print(item_id, stock['stock'])
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


async def create_loss(loss_list):
    organization_meta = await get_organization()
    positions_list = []
    for item in loss_list:
        print(f'Позиция {item[0]} удалена')
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
    print(req_data)
    async with aiohttp.ClientSession(headers={'Authorization': token, 'Content-Type': 'application/json'}) as session:
        await session.post(f'https://online.moysklad.ru/api/remap/1.2/entity/loss', data=req_data)
    print(f'Запрос на удаление отправлен')
