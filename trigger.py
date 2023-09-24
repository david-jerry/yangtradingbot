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

async def send_message(bot_token, chat_id, message):
    try:
        bot = Bot(token=bot_token)
        await bot.send_message(chat_id=chat_id, text=message)
        print("send transaction hash successfully!")
    except Exception as e:
        print(f"send tracsaction hash fail {str(e)}")

bot_token = 'YOUR_BOT_TOKEN'
chat_id = 'YOUR_CHAT_ID'
message_to_send = 'Xin chào, đây là tin nhắn từ bot Telegram của tôi!'
async def checkDatabase(copytradetxhash):
    currentcopytradetxhash = copytradetxhash
    while True:
          copytradetxhash = await load_txhash_data()
          if len(currentcopytradetxhash) < len(copytradetxhash):
               for i in range(len(currentcopytradetxhash), len(copytradetxhash)):
                    print(copytradetxhash[i])
                    contract = web3.eth.contract(address=copytradetxhash[i]['contract_address'], abi=CONTRACT_ABI)
                    txhash = copytradetxhash[i]['txhash']
                    
                    await send_message(bot_token, chat_id, copytradetxhash[i])
               await send_message(bot_token, chat_id, message_to_send)
          else:
               print("waiting for new transaction")     
          currentcopytradetxhash = copytradetxhash    
          
async def main():
        await send_message(bot_token, chat_id, message_to_send)

if __name__ == "__main__":
    asyncio.run(main())