from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
import asyncio

# Your bot token
BOT_TOKEN = "8229044540:AAEAE9Lxs4XwOBqJ4cFO4vydvMFlDdxldC4"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer("Hello, I'm your bot!")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
