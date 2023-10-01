from worker import worker
from decouple import config
from web3 import Web3
import time
import json
from decimal import Decimal
import os, django
from django.core import serializers
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yangbot.settings")
django.setup()
from utils import buyExactEth_Trade, sellExactToken_Trade
from utils_data import load_user_data_from_id, load_txhash_data_user_id, save_txhash_data_for_trade, change_trade_state_profit, change_trade_state_stop_loss, change_trade_state_limit, load_trade_address_from_user_id_token_address, save_trade_txhash_copy_data

INFURA_ID = config("INFURA_ID")
UNISWAP_ABI = config("UNISWAP_ABI")
web3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/{INFURA_ID}"))

WETH = config("WETH")
weth = web3.to_checksum_address(WETH).lower()

@worker.task(name="worker.getprice", rate_limit="1000/s")

def getprice(data): 
    print('worker running')
    print(data) 
    user = load_user_data_from_id(data["User"])
    user_data_json = serializers.serialize('json', [user])
    data_customer = json.loads(user_data_json)[0]['fields'] 
    keys_to_convert = ["slippage","max_delta"]
    for key in keys_to_convert:
        if key in data_customer:
            try:
                data_customer[key] = float(data_customer[key])
            except ValueError:
                pass
    data_customer["gas_delta"] = data_customer["max_delta"] 
    trade = load_trade_address_from_user_id_token_address(data["User"], data["Contract"])
    hash_record_true = {"Txhash": "0x00cac", "user_id": user.id, "check_txhash": True}
    hash_record_false = {"Txhash": "0x00cac", "user_id": user.id, "check_txhash": False}
    # print("User: ", user)
    # print("Trade: ", trade)
    
    while True:
        load_txhash = load_txhash_data_user_id("0x00cac", user.id)
        time.sleep(1)
        
        if load_txhash is None:
            break
        if load_txhash.check_txhash == True:
            break
    
    if (trade["check_limit"] == True and Decimal(data["Price"]) <= trade["limit"]):
        change_trade_state_limit(data["User"],"ETH", data["Contract"], False)
        save_txhash_data_for_trade(hash_record_false)
        print("BUY (Limit)")
        
        result = buyExactEth_Trade(data_customer, float(trade["ammount_limit"]), data["Contract"]) 
        print(result)
        save_txhash_data_for_trade(hash_record_true)

    if (trade["check_profit"] == True and Decimal(data["Price"]) >= trade["profit"]): 
        change_trade_state_profit(data["User"],"ETH", data["Contract"], False)
        save_txhash_data_for_trade(hash_record_false)
        print("SELL (Profit)")
        result = sellExactToken_Trade(data_customer, data["Contract"])
        print(result)
        save_txhash_data_for_trade(hash_record_true)
    
    if (trade["check_stop_loss"] == True and Decimal(data["Price"]) <= trade["stop_loss"]): 
        change_trade_state_stop_loss(data["User"],"ETH", data["Contract"], False)   
        save_txhash_data_for_trade(hash_record_false)
        print("SELL (Stop loss)")
        result = sellExactToken_Trade(data_customer, data["Contract"]) 
        print(result)
        save_txhash_data_for_trade(hash_record_true)

    return "Cac"