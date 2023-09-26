import json
from web3 import Web3
import asyncio
from decouple import config
from tasks import copytrade
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

from utils_data import load_copy_trade_addresses_chain, save_txhash_data
from uniswap_universal_router_decoder import RouterCodec
contract_abi = config("CONTRACT_ABI")

async def log_loop(event_filter, poll_interval):
    startblock = latest_block = web3.eth.get_block("latest")["number"]
    startblock = 0
    # latest_block = 18219263
    # latest_block = 
    while True:
        try:
            objet_userid_address_list = await load_copy_trade_addresses_chain("ETH")
            user_id_list = []
            address_list = []
            for object_userid_address in objet_userid_address_list:
                user_id_list.append(object_userid_address.user_id)
                address_list.append(object_userid_address.contract_address)
            # print(user_id_list, address_list)

            latest_block = web3.eth.get_block("latest")["number"]
            print("startBlock: ", startblock, "latest_block: ", latest_block)
            for i in range(len(address_list)):
                retries = 0
                address = address_list[i]
                # address = "0xfA7A0232958938202039F4E35216cEA65971F876"
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
                print("address:", address_list[i])
                while retries < 10:
                    response = requests.get(ETHERSCAN_ENDPOINT, params=api_params)

                    if response.status_code == 200 and response.content:
                        break  # Request was successful, exit the retry loop

                    print(f"Request {retries} of {address} failed with status code {response.status_code}. Retrying in 0.4 seconds...")
                    retries += 1
                    time.sleep(0.4)
                
                if retries == 10:
                    print(f"Maximum number of retries reached. Request of {address} could not be completed.")
                elif response.json()["status"] == "1":
                    handle_event(response.json())
                # await asyncio.sleep(0.4)
                time.sleep(0.4)

            startblock = latest_block
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error: {e}")
            # Wait for a while and then retry
            await asyncio.sleep(poll_interval)


def handle_event(event):
    # print(event)
    for i in range(len(event["result"])):
        print(event["result"][i]["hash"])
        input_data = event["result"][i]['input']
        # print(input_data)
        _to = event["result"][i]["to"].lower()
        print(_to)
        print(UNIVERSAL_ROUTER.lower())
        if (_to.lower() != UNIVERSAL_ROUTER.lower()):
            print("Not UNIVERSAL_ROUTER contract")
            continue
        # decoded_inputs = web3.eth.contract(abi=UNISWAP_ABI).decode_function_input(input_data)
        codec = RouterCodec(w3=web3)
        decoded_trx_input = codec.decode.function_input(input_data)
        # print(decoded_trx_input[1]["inputs"][1][1]['path'])
        _from = event["result"][i]["from"]
        # print("From: ", _from)
        _hash = event["result"][i]["hash"]
        # print("Hash: ", _hash)
        # print(decoded_trx_input[1]["inputs"][1][0].fn_name)
        if (decoded_trx_input[1]["inputs"][1][0].fn_name not in ["V2_SWAP_EXACT_IN"]):
            print("Not SWAP ROUTER V2 method")
            continue
        print("-------------------------------------------------------------")
        data = {
            "_from": _from,
            "_to": _to,
            "_hash": _hash,
            "_path": decoded_trx_input[1]["inputs"][1][1]['path']
        }
        copytrade.apply_async(args=[data], queue="tc-queue1")
        print(data)
        # print(result)
        # return _hash
        # copytrade.send_task('worker.copytrade', args=[data], queue="tc-queue1")


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
