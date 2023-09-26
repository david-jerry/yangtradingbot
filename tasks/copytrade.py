from worker import worker
from decouple import config
from web3 import Web3
import time
import json
import os, django
from django.core import serializers
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yangbot.settings")
django.setup()
from utils import buyExactEth,sellExactToken
from utils_data import load_copytrade_address_user_data_id, save_txhash_data, load_txhash_data, load_copy_trade_addresses_copy, address_to_id, load_user_data_id

INFURA_ID = config("INFURA_ID")
UNISWAP_ABI = config("UNISWAP_ABI")
web3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/{INFURA_ID}"))

WETH = config("WETH")
weth = web3.to_checksum_address(WETH).lower()

@worker.task(name="worker.copytrade", rate_limit="1000/s")
# async def copytrade(data): 
#     print(data)
#     result = await save_txhash_data(data['_hash'])
#     print(result)
#     return "Cac"

def copytrade(data): 
    print('worker running')
    hash_record = {"Txhash": data['_hash']}
    check_duplicate = load_txhash_data(hash_record['Txhash'])
    pair_contract = data["_path"]
    # print(check_duplicate)
    if (check_duplicate is None):
        result = save_txhash_data(hash_record)
        # print("SAVE: ", result)
        trade = load_copy_trade_addresses_copy(data["_from"])
        if (trade is not None):
            list_user_id = address_to_id(data["_from"])
            list_user_data =[]
            for user_id in list_user_id:
                user = load_user_data_id(user_id)
                list_user_data.append((user, load_copytrade_address_user_data_id(data['_from'], user.id)))
            for user_data in list_user_data:
                data = {}
                # print(user_data)

                user_data_json = serializers.serialize('json', [user_data[0]])
                data_customer = json.loads(user_data_json)[0]['fields'] 
                keys_to_convert = ["wallet_gas", "eth_balance", "bsc_balance", "arp_balance", "base_balance", "max_gas", "max_gas_price", "max_delta", "slippage", "buy_tax", "sell_tax", "sell_hi", "sell_lo", "sell_hi_amount","sell_lo_amount"]
                for key in keys_to_convert:
                    if key in data_customer:
                        try:
                            data_customer[key] = float(data_customer[key])
                        except ValueError:
                            pass
                # print(data_customer)

                user_data_json = serializers.serialize('json', [user_data[1]])
                data_copytrade = json.loads(user_data_json)[0]['fields'] 
                keys_to_convert = ["amount", "slippage", "gas_delta", "sell_hi_amount","sell_lo_amount","sell_hi","sell_lo", "max_buy_tax","max_sell_tax"]
                for key in keys_to_convert:
                    if key in data_copytrade:
                        try:
                            data_copytrade[key] = float(data_copytrade[key])
                        except ValueError:
                            pass
                pair_contract[0] = pair_contract[0].lower()
                pair_contract[1] = pair_contract[1].lower()
                # print(pair_contract)
                if (pair_contract[0] in weth):
                    # result = buyExactEth(data_customer, data_copytrade, pair_contract[1])
                    # print("BUY Tokens---------------: ", result)
                    print("BUY Tokens+++++++++++++++++++++")
                else:
                    sellExactToken(data_customer, data_copytrade, pair_contract[0])
                    # print("SELL Tokens---------------: " , result)
                    print("SELL Tokens+++++++++++++++++++")
        else:
            return "TRADE NOT EXIST"
    else:
        return "TXHASH EXIST!"

    # print(result)
    return "Cac"