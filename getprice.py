import json
from web3 import Web3
import asyncio
from decimal import Decimal
from decouple import config
from tasks import getprice
import time 

infura_url = config("PUBLICRPC")
web3 = Web3(Web3.HTTPProvider(infura_url))
import requests

address = "0x8BF2405f5848db6dD2B8041456f73550c8d78E78"
lastestBlock = web3.eth.get_block("latest")["number"]
startBlock = 9737693
import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yangbot.settings")
django.setup()
ETHERAPI = config("ETHERAPI")
ETHERSCAN_ENDPOINT = config("ETHERSCAN_ENDPOINT")
UNISWAP_ROUTER =config("UNISWAP_ROUTER")
UNIVERSAL_ROUTER =config("UNIVERSAL_ROUTER")
UNISWAP_ABI = config("UNISWAP_ABI")
DEXSCREENER_ENDPOINT = config("DEXSCREENER_ENDPOINT")
WETH = config("WETH").lower()
UNISWAP_FACTORY_ABI = config("UNISWAP_FACTORY_ABI")
UNISWAP_FACTORY= config("UNISWAP_FACTORY").lower()
from utils_data import load_token_addresses_all_from_trade_address
from uniswap_universal_router_decoder import RouterCodec
contract_abi = config("CONTRACT_ABI")

async def log_loop(event_filter, poll_interval):
    uniswap_factory_address = web3.to_checksum_address(UNISWAP_FACTORY)
    uniswap_factory = web3.eth.contract(address=uniswap_factory_address, abi=UNISWAP_FACTORY_ABI)
    weth = web3.to_checksum_address(WETH)
    startblock = latest_block = web3.eth.get_block("latest")["number"]
    while True:
        try:
            list_trade = await load_token_addresses_all_from_trade_address("ETH")
            print(list_trade)
            for trade in list_trade:
                trade.token_address = trade.token_address.lower()
                token_address = web3.to_checksum_address(trade.token_address)
                pair = uniswap_factory.functions.getPair(token_address, weth).call()
                response = requests.get(f"{DEXSCREENER_ENDPOINT}{pair}")
                handle_event(response.json(), trade)
            await asyncio.sleep(poll_interval)
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error: {e}")
            # Wait for a while and then retry
            await asyncio.sleep(poll_interval)


def handle_event(event, trade):
    print("PRICE: ", event["pairs"][0]["priceUsd"])
    print("USER: ", trade)
    data = {
        "Price": Decimal(event["pairs"][0]["priceUsd"]),
        "User": trade.user,
        "Contract": trade.token_address.lower(),
    }
    result = getprice.apply_async(args=[data], queue="tc-queue2")
    print("Cac")

def main():
    print("Listening for events...")
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(asyncio.gather(log_loop(0, 5)))
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()


if __name__ == "__main__":
    main()
