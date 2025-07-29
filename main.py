import logging
import os
from aiogram import Bot, Dispatcher, types
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from aiogram.utils import executor

# Load environment variables (like your BOT_TOKEN)
load_dotenv()
API_TOKEN = os.getenv("BOT_TOKEN")

# Set up bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Set up FastAPI app for the webhook
app = FastAPI()

# Set up logging
logging.basicConfig(level=logging.INFO)

# This handler will be triggered when the user types "/start"
@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    await message.reply("Hello! I am your webhook Telegram bot. How can I help you today?")

# Webhook handler to process the incoming updates from Telegram
@app.post("/webhook")
async def handle_webhook(request: Request):
    data = await request.json()  # Receive the incoming update
    update = types.Update(**data)  # Parse it into aiogram's Update format
    await dp.process_update(update)  # Pass it to aiogram's Dispatcher
    return {"ok": True}

# Set the webhook URL on bot startup
@app.on_event("startup")
async def on_startup():
    webhook_url = "https://your-app-name.onrender.com/webhook"  # Set your Render app URL here
    await bot.set_webhook(webhook_url)  # Set the webhook for Telegram to send updates to

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
