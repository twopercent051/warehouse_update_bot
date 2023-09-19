from dataclasses import dataclass
from environs import Env
import logging


logger = logging.getLogger(__name__)
console_out = logging.StreamHandler()
logging.basicConfig(level=logging.INFO)

@dataclass
class GConfig:
    ozon_token: str
    ms_token: str
    recht_login: str
    recht_psw: str
    unas_url: str

    tlg_token: str
    tlg_admin: str


@dataclass
class Config:
    g_conf: GConfig


def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    return Config(
        g_conf=GConfig(
            ozon_token=env.str('OZON_TOKEN'),
            ms_token=env.str('MS_TOKEN'),
            recht_login=env.str('RECHT_LOGIN'),
            recht_psw=env.str('RECHT_PSW'),
            tlg_token=env.str("TLG_TOKEN"),
            tlg_admin=env.str("TLG_ADMIN"),
            unas_url=env.str("UNAS_URL"),
        )
    )
