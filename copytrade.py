import json
from web3 import Web3
import asyncio
from decouple import config
from tasks import copytrade

infura_url = config("PUBLICRPC")
web3 = Web3(Web3.HTTPProvider(infura_url))
import requests

address = "0x8BF2405f5848db6dD2B8041456f73550c8d78E78"
lastestBlock = web3.eth.get_block("latest")["number"]
startBlock = 9737693
ETHERAPI = config("ETHERAPI")
ETHERSCAN_ENDPOINT = config("ETHERSCAN_ENDPOINT")
import django, os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yangbot.settings")
django.setup()
from utils_data import load_copy_trade_addresses_chain, save_txhash_data

abi = [
    {
        "inputs": [
            {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
            {"internalType": "address[]", "name": "path", "type": "address[]"},
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "deadline", "type": "uint256"},
        ],
        "name": "swapExactETHForTokens",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function",
    }
]


async def log_loop(event_filter, poll_interval):
    startblock = latest_block = web3.eth.get_block("latest")["number"]

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
                address = address_list[i]
                api_params = {
                    "module": "account",
                    "action": "txlist",
                    "address": address,
                    "startblock": startblock-1,
                    "endblock": latest_block,
                    "page": 1,
                    "offset": 50,
                    "apikey": ETHERAPI,
                }
                print("address: ", address_list[i])
                response = requests.get(ETHERSCAN_ENDPOINT, params=api_params)
                if response.json()["status"] == "1":
                    handle_event(response.json())
                    # _hash = handle_event(response.json())
                    # hash_record = {"Txhash": _hash}
                    # save_hash = await save_txhash_data(hash_record)
                    # print("SAVE HASH: ", save_hash)
                await asyncio.sleep(0.3)
            startblock = latest_block
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error: {e}")
            # Wait for a while and then retry
            await asyncio.sleep(poll_interval)


def handle_event(event):
    # print("handle_event")
    input_data = event["result"][0]['input']
    decoded_inputs = web3.eth.contract(abi=abi).decode_function_input(input_data)
    _from = event["result"][0]["from"]
    # print("From: ", _from)
    _to = event["result"][0]["to"]
    # print("To: ", _to)
    _hash = event["result"][0]["hash"]
    # print("Hash: ", _hash)
    print("-------------------------------------------------------------")
    data = {
        "_from": _from,
        "_to": _to,
        "_hash": _hash,
        "_path": decoded_inputs[1]["path"]
    }
    copytrade.apply_async(args=[data], queue="tc-queue1")
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
