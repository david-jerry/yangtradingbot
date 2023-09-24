import asyncio
from telegram import Bot

async def send_message(bot_token, chat_id, message):
    try:
        bot = Bot(token=bot_token)
        await bot.send_message(chat_id=chat_id, text=message)
        print("Đã gửi tin nhắn thành công!")
    except Exception as e:
        print(f"Gửi tin nhắn thất bại: {str(e)}")

bot_token = 'YOUR_BOT_TOKEN'
chat_id = 'YOUR_CHAT_ID'
message_to_send = 'Xin chào, đây là tin nhắn từ bot Telegram của tôi!'
async def main():
    w
    await send_message(bot_token, chat_id, message_to_send)

if __name__ == "__main__":
    asyncio.run(main())