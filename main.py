import os
import httpx
import asyncio
import json
from dotenv import load_dotenv
from fastapi import FastAPI, Request

# --- Configuration and Initialization ---

load_dotenv() # Load environment variables from the .env file.

BOT_TOKEN = os.getenv("BOT_TOKEN") # Get your bot token from environment variables.
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set. Please get your token from BotFather and add it to a .env file.")

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}" # Base URL for Telegram Bot API calls.

app = FastAPI() # Initialize the FastAPI application.

# --- Telegram API Interaction Functions ---

async def send_message(chat_id: int, text: str):
    """
    Asynchronously sends a message to a specific chat on Telegram.
    """
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{API_URL}/sendMessage", json=payload)
            response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx).
            print(f"Message sent to {chat_id}: {text}")
    except httpx.RequestError as e:
        print(f"Error sending message (request error): {e}")
    except httpx.HTTPStatusError as e:
        print(f"Error response {e.response.status_code} while sending message: {e.response.text}")

# --- FastAPI Webhook Endpoints ---

@app.get("/")
async def health_check():
    """
    A simple GET endpoint to confirm the bot server is running. Useful for Render's health checks.
    """
    return {"status": "ok", "message": "Bot server is running!"}

@app.post("/webhook")
async def telegram_webhook(request: Request):
    """
    This POST endpoint receives updates from Telegram via webhook.
    """
    update = await request.json() # Parse the incoming JSON update from Telegram.
    print(f"Received Telegram update: {json.dumps(update, indent=2)}") # Log the full update for debugging.

    # Check if the update contains a 'message'.
    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"] # Get the chat ID to send the response to.
        text = message.get("text", "") # Get the text of the message, handling cases where it might not exist.

        # --- Core Logic: Respond to /start command ---
        if text == "/start":
            response_text = "Welcome! I am your simple bot. How can I assist you today?"
            await send_message(chat_id, response_text)
            print(f"Responded to /start from {chat_id}")
        else:
            # You can add logic here for other commands or general messages.
            # For now, it just acknowledges non-/start messages.
            await send_message(chat_id, "I only understand the /start command for now. Try it!")
            print(f"Responded to non-/start message from {chat_id}")

    # Always return a 200 OK status to Telegram to confirm successful receipt of the update.
    return {"status": "ok"}

# --- How to Run This Bot ---
# 1. Save this code as `main.py` (or any other .py file, e.g., `my_bot.py`).
# 2. Make sure you have a `.env` file in the same directory containing:
#    BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN_HERE"
# 3. Ensure you have installed the necessary libraries:
#    pip install fastapi uvicorn httpx python-dotenv
#
# To run locally for testing (FastAPI will start a local web server):
#    uvicorn main:app --reload
#    (If your file is named `my_bot.py`, use `uvicorn my_bot:app --reload`)
#    For local testing, you would typically use a tool like ngrok to expose your
#    local server to the internet, then set your webhook URL to the ngrok URL.
#
# For deployment on Render:
#    Your 'Start Command' in Render should be:
#    uvicorn main:app --host 0.0.0.0 --port $PORT
#    (Again, change `main` to your file name if different).
#    Remember to set the `BOT_TOKEN` environment variable directly in Render's dashboard.
#    After deployment, you need to run your `set_webhook.py` script once,
#    using your Render service's public URL (e.g., `https://your-bot-name.onrender.com/webhook`).
