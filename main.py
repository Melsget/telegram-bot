from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
import asyncio

# Your bot token
BOT_TOKEN = "PUT_YOUR_TOKEN_HERE"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer("Hello, I'm your bot!")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
