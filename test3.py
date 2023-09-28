import json
from web3 import Web3
import asyncio
from decouple import config
from tasks import copytrade

infura_url = config("PUBLICRPC")
web3 = Web3(Web3.HTTPProvider(infura_url))
import requests

import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yangbot.settings")
django.setup()
ETHERAPI = config("ETHERAPI")
ETHERSCAN_ENDPOINT = config("ETHERSCAN_ENDPOINT")
UNISWAP_ROUTER =config("UNISWAP_ROUTER")
UNISWAP_ABI = config("UNISWAP_ABI")
ROUTER_ABI = config("ROUTER_ABI")
from utils_data import load_copy_trade_addresses_chain, save_txhash_data
from uniswap_universal_router_decoder import RouterCodec
contract_abi = config("CONTRACT_ABI")
address = "0xe09D878d1b6a32b43d3a1A283Eb1e8E970210595" 
async def log_loop(event_filter, poll_interval):
    # startblock = latest_block = web3.eth.get_block("latest")["number"]
    startblock = 18226876
    latest_block = 18226888
    while True:
        try:
            # objet_userid_address_list = await load_copy_trade_addresses_chain("ETH")

            api_params = {
                            "module": "account",
                            "action": "txlist",
                            "address": address,
                            "startblock": startblock,
                            "endblock": latest_block,
                            "page": 1,
                            "offset": 50,
                            "apikey": ETHERAPI,
                        }
            response = requests.get(ETHERSCAN_ENDPOINT, params=api_params)
            input_data = response.json()["result"][0]['input']
            print(input_data)
            # decoded_inputs = web3.eth.contract(abi=ROUTER_ABI).decode_function_input(input_data)
            codec = RouterCodec(w3=web3)
            decoded_trx_input = codec.decode.function_input(input_data)
            # print(decoded_trx_input[0])
            print(decoded_trx_input)
            print(decoded_trx_input[1]["inputs"][1][0].fn_name)
            print(decoded_trx_input[1]["inputs"][1][1]['path'])
            await asyncio.sleep(0.4)

            startblock +=1
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error: {e}")
            # Wait for a while and then retry
            await asyncio.sleep(poll_interval)


def main():
    print("Listening for events...")
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(asyncio.gather(log_loop(0, 1)))
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()


if __name__ == "__main__":
    main()
