import asyncio
import requests
from decouple import config
from web3 import Web3
INFURA_URL = config("INFURA_URL")
web3 = Web3(Web3.HTTPProvider(INFURA_URL))
CONTRACT_ABI = config("CONTRACT_ABI")
from telegram import Bot
import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yangbot.settings")
django.setup()
from utils_data import load_txhash_data
TOKEN = config("TOKEN")
async def send_message(bot_token, chat_id, message):
    try:
        bot = Bot(token=bot_token)
        await bot.send_message(chat_id=chat_id, text=message)
        print("send transaction hash successfully!")
    except Exception as e:
        print(f"send tracsaction hash fail {str(e)}")


async def checkDatabase(bot_token):
    currentcopytradetxhash = copytradetxhash = await load_txhash_data()
    while True:      
          copytradetxhash = await load_txhash_data()
          if len(currentcopytradetxhash) < len(copytradetxhash):
               for i in range(len(currentcopytradetxhash), len(copytradetxhash)):
                    print(copytradetxhash[i])
                    chat_id = copytradetxhash[i]['user_id']
                    contract = web3.eth.contract(address=copytradetxhash[i]['contract_address'], abi=CONTRACT_ABI)
                    txhash = copytradetxhash[i]['txhash']
                    txhash = "https://etherscan.io/tx/" + txhash
                    botname = copytradetxhash[i]['bot_name']
                    symbol = contract.functions.symbol().call()
                    name = contract.functions.name().call()
                    amount = copytradetxhash[i]['amount']
                    amount = web3.from_wei(amount, 'ether')
                    fullmessage = f'Copy trade from {botname} amount {amount} ${symbol} {name} \n Explorer: {txhash}'
                    await send_message(bot_token, chat_id, fullmessage)
          else:
               print("waiting for new transaction") 
          
async def main():
        checkDatabase(TOKEN)
if __name__ == "__main__":
    asyncio.run(main())