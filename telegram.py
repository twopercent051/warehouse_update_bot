import asyncio

import aiohttp

from config import load_config

config = load_config(".env")
token = config.g_conf.tlg_token
admin = config.g_conf.tlg_admin


async def message(text: str):
    params = {
        "chat_id": admin,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": "true"
    }
    async with aiohttp.ClientSession() as session:
        await session.get(f'https://api.telegram.org/bot{token}/sendMessage', params=params)


