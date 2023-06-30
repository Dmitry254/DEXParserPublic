import traceback

import requests
import json
from datetime import datetime
from web3 import Web3
from web3.middleware import geth_poa_middleware

from base_func import get_data

private_key = ""
my_address = ""
contract_address = ""
bsc_scan_api = ""

bsc = ""
bsc_wss = ""


def set_http_web3(bsc=bsc):
    web3 = Web3(Web3.HTTPProvider(bsc))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    return web3


def set_wss_web3():
    web3 = Web3(Web3.WebsocketProvider(bsc_wss, websocket_timeout=360, websocket_kwargs={"max_size": 650000000}))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    return web3


def get_contract(web3, contract_address):
    abi_endpoint = f"https://api.bscscan.com/api?module=contract&action=getabi&address={contract_address}&apikey={bsc_scan_api}"
    abi = json.loads(requests.get(abi_endpoint).text)
    contract = web3.eth.contract(contract_address, abi=abi["result"])
    return contract