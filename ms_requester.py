import asyncio
import math
from typing import Literal, List

import aiohttp
import json
from config import load_config, logger

config = load_config(".env")
token = config.g_conf.ms_token


class MSApi:

    def __init__(self):
        self.organization_meta = {
            'meta': {
                'href': 'https://api.moysklad.ru/api/remap/1.2/entity/organization/fdcd9b68-90c3-11ed-0a80'
                        '-070b0009f544',
                'metadataHref': 'https://api.moysklad.ru/api/remap/1.2/entity/organization/metadata',
                'type': 'organization',
                'mediaType': 'application/json',
                'uuidHref': 'https://api.moysklad.ru/app/#mycompany/edit?id=fdcd9b68-90c3-11ed-0a80-070b0009f544'
            }
        }
        # self.organization_meta = {'meta': {
        #     'href': 'https://api.moysklad.ru/api/remap/1.2/entity/organization/bdfcb529-0439-11ec-0a80-0849003936ac',
        #     'metadataHref': 'https://api.moysklad.ru/api/remap/1.2/entity/organization/metadata',
        #     'type': 'organization', 'mediaType': 'application/json',
        #     'uuidHref': 'https://online.moysklad.ru/app/#mycompany/edit?id=bdfcb529-0439-11ec-0a80-0849003936ac'}}

        self.recht_stock = {
            'meta': {
                'href': 'https://api.moysklad.ru/api/remap/1.2/entity/store/fdcec3ea-90c3-11ed-0a80-070b0009f546',
                'metadataHref': 'https://api.moysklad.ru/api/remap/1.2/entity/store/metadata',
                'type': 'store',
                'mediaType': 'application/json',
                'uuidHref': 'https://api.moysklad.ru/app/#warehouse/edit?id=fdcec3ea-90c3-11ed-0a80-070b0009f546'
            }
        }
        # self.recht_stock = {
        #     'meta': {
        #         'href': 'https://api.moysklad.ru/api/remap/1.2/entity/store/bdfdf45d-0439-11ec-0a80-0849003936ae',
        #         'metadataHref': 'https://api.moysklad.ru/api/remap/1.2/entity/store/metadata',
        #         'type': 'store',
        #         'mediaType': 'application/json',
        #         'uuidHref': 'https://online.moysklad.ru/app/#warehouse/edit?id=bdfdf45d-0439-11ec-0a80-0849003936ae'
        #     }}

        self.office_stock = {
            'meta': {
                'href': 'https://api.moysklad.ru/api/remap/1.2/entity/store/d4f77c31-912d-11ed-0a80-0e1700025bbd',
                'metadataHref': 'https://api.moysklad.ru/api/remap/1.2/entity/store/metadata',
                'type': 'store',
                'mediaType': 'application/json',
                'uuidHref': 'https://api.moysklad.ru/app/#warehouse/edit?id=d4f77c31-912d-11ed-0a80-0e1700025bbd'
            }
        }
        # self.office_stock = {
        #     'meta': {
        #         'href': 'https://api.moysklad.ru/api/remap/1.2/entity/store/c34ca5a9-5660-11ee-0a80-05a10001f45f',
        #         'metadataHref': 'https://api.moysklad.ru/api/remap/1.2/entity/store/metadata',
        #         'type': 'store',
        #         'mediaType': 'application/json',
        #         'uuidHref': 'https://online.moysklad.ru/app/#warehouse/edit?id=c34ca5a9-5660-11ee-0a80-05a10001f45f'
        #     }}

        # self.unas_stock = {
        #     'meta': {
        #         'href': 'https://api.moysklad.ru/api/remap/1.2/entity/store/d3ba8b81-5660-11ee-0a80-05a10001f4e2',
        #         'metadataHref': 'https://api.moysklad.ru/api/remap/1.2/entity/store/metadata',
        #         'type': 'store',
        #         'mediaType': 'application/json',
        #         'uuidHref': 'https://online.moysklad.ru/app/#warehouse/edit?id=d3ba8b81-5660-11ee-0a80-05a10001f4e2'
        #     }}

        self.unas_stock = {
            'meta': {
                'href': 'https://api.moysklad.ru/api/remap/1.2/entity/store/f7d8c159-5d2c-11ee-0a80-02e6000f5174',
                'metadataHref': 'https://api.moysklad.ru/api/remap/1.2/entity/store/metadata',
                'type': 'store',
                'mediaType': 'application/json',
                'uuidHref': 'https://online.moysklad.ru/app/#warehouse/edit?id=f7d8c159-5d2c-11ee-0a80-02e6000f5174'
            }}

    @staticmethod
    async def get_token():
        async with aiohttp.ClientSession(
                headers={'Authorization': "Basic CQphZG1pbkB0d29wZXJjZW50MDUxOmlrRmtqRVdDNA==",
                         'Content-Type': 'application/json', "Accept-Encoding": "gzip"}) as session:
            async with session.post(f'https://api.moysklad.ru/api/remap/1.2/security/token') as resp:
                response = await resp.read()
                print(response)

    @staticmethod
    async def __send_get(url: str):
        async with aiohttp.ClientSession(headers={'Authorization': token, "Accept-Encoding": "gzip"}) as session:
            async with session.get(url=url) as resp:
                response = await resp.read()
            return json.loads(response)

    async def get_stock(self):
        url = "https://api.moysklad.ru/api/remap/1.2/entity/store"
        data = await self.__send_get(url=url)
        rows = data["rows"]
        return dict(meta=rows)

    async def get_organization(self):
        url = "https://api.moysklad.ru/api/remap/1.2/entity/organization"
        data = await self.__send_get(url=url)
        meta = data["rows"][0]["meta"]
        return dict(meta=meta)

    async def __get_products(self):
        url = "https://api.moysklad.ru/api/remap/1.2/entity/product"
        data = await self.__send_get(url=url)
        size = data["meta"]["size"]
        pages = math.ceil(size / 1000)
        res_list = []
        for i in range(pages):
            offset = i * 1000
            url = f"https://api.moysklad.ru/api/remap/1.2/entity/product?offset={offset}"
            data = await self.__send_get(url=url)
            for item in data["rows"]:
                item_art = item['article']
                item_id = item['id']
                res_tuple = (item_art, item_id)
                res_list.append(res_tuple)
        return res_list, size

    async def get_current(self) -> dict:
        products_tuple = await self.__get_products()
        product_list = products_tuple[0]
        size = products_tuple[1]
        pages = math.ceil(size / 1000)
        office_list = []
        recht_list = []
        recht_item_list = []
        unas_list = []
        unas_item_list = []
        for i in range(pages):
            offset = i * 1000
            url = f"https://api.moysklad.ru/api/remap/1.2/report/stock/bystore?offset={offset}"
            data = await self.__send_get(url=url)
            data = data["rows"]
            for item in data:
                item_id = item['meta']['href'].split('/')[-1].split('?')[0]
                for stock in item['stockByStore']:
                    if stock['meta']['href'] == self.office_stock['meta']['href'] and stock['stock'] > 0:
                        for prod in product_list:
                            if item_id == prod[1]:
                                item_art = prod[0]
                                res_dict = dict(item_id=item_id,
                                                item_art=item_art,
                                                stock=int(stock["stock"]),
                                                reserve=int(stock["reserve"]))
                                office_list.append(res_dict)
                                break
                    if stock['meta']['href'] == self.recht_stock['meta']['href']:
                        for prod in product_list:
                            if item_id == prod[1]:
                                item_art = prod[0]
                                res_dict = dict(item_id=item_id,
                                                item_art=item_art,
                                                stock=int(stock["stock"]),
                                                reserve=int(stock["reserve"]))
                                recht_item_list.append(item_id)
                                recht_list.append(res_dict)
                                break
                    if stock['meta']['href'] == self.unas_stock['meta']['href']:
                        for prod in product_list:
                            if item_id == prod[1]:
                                item_art = prod[0]
                                res_dict = dict(item_id=item_id,
                                                item_art=item_art,
                                                stock=int(stock["stock"]),
                                                reserve=int(stock["reserve"]))
                                unas_item_list.append(item_id)
                                unas_list.append(res_dict)
                                break
        for prod in product_list:
            item_prefix = prod[0].split("-")[0]
            if item_prefix == "РСВ-":
                if prod[1] not in recht_item_list:
                    recht_list.append(dict(item_id=prod[1], item_art=prod[0], stock=0, reserve=0))
            else:
                if prod[1] not in unas_item_list:
                    unas_list.append(dict(item_id=prod[1], item_art=prod[0], stock=0, reserve=0))
        return dict(office=office_list, recht=recht_list, unas=unas_list)

    async def stock_operation(self,
                              type_operation: Literal["enter", "loss"],
                              stock_type: Literal["recht", "unas"],
                              item_list: List[tuple]):
        positions_list = []
        for item in item_list:
            meta = dict(href=f"https://api.moysklad.ru/api/remap/1.2/entity/product/{item[0]}",
                        metadataHref="https://api.moysklad.ru/api/remap/1.2/entity/product/metadata",
                        type="product",
                        mediaType="application/json")
            item_dict = dict(quantity=item[1], assortment=dict(meta=meta))
            if type_operation == "enter":
                item_dict["assortment"]["price"] = item[2]
            positions_list.append(item_dict)
        stock_dict = dict(recht=self.recht_stock, unas=self.unas_stock)
        request_data = dict(organization=self.organization_meta,
                            store=stock_dict[stock_type],
                            positions=positions_list)
        request_data = json.dumps(request_data)
        operation_dict = dict(enter="Оприходовано", loss="Списано")
        async with aiohttp.ClientSession(
                headers={'Authorization': token, 'Content-Type': 'application/json'}) as session:
            await session.post(f'https://api.moysklad.ru/api/remap/1.2/entity/{type_operation}', data=request_data)
        logger.info(f'{operation_dict[type_operation]} {len(item_list)} позиций')


if __name__ == "__main__":
    api = MSApi()
    a = asyncio.run(api.get_stock())
    print(a)
