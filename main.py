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
    # This will cause the application to fail if BOT_TOKEN is not set,
    # which is good for immediate feedback during deployment.
    raise ValueError("BOT_TOKEN environment variable not set. Please get your token from BotFather and add it to a .env file locally, or set it in Render's environment variables.")

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}" # Base URL for Telegram Bot API calls.

# --- FastAPI Application Instance ---
# THIS IS THE CRITICAL LINE: It creates the FastAPI application instance
# that Uvicorn looks for. Ensure this line is present and not commented out.
app = FastAPI()

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
            print(f"Message sent to {chat_id}: {text}") # Log successful sends
    except httpx.RequestError as e:
        print(f"Error sending message (request error): {e}")
    except httpx.HTTPStatusError as e:
        print(f"Error response {e.response.status_code} while sending message: {e.response.text}")

# --- FastAPI Webhook Endpoints ---

@app.get("/")
async def health_check():
    """
    A simple GET endpoint to confirm the bot server is running.
    When you visit your Render URL (e.g., https://your-bot.onrender.com),
    you should see {"status":"ok","message":"Bot server is running!"}
    """
    return {"status": "ok", "message": "Bot server is running!"}

@app.post("/webhook")
async def telegram_webhook(request: Request):
    """
    This POST endpoint receives updates from Telegram via webhook.
    Telegram sends a JSON payload to this URL whenever there's an update for your bot.
    """
    try:
        update = await request.json() # Parse the incoming JSON update from Telegram.
        print(f"Received Telegram update: {json.dumps(update, indent=2)}") # Log the full update for debugging.

        # Check if the update contains a 'message'.
        if "message" in update:
            message = update["message"]
            chat_id = message["chat"]["id"] # Get the chat ID to send the response to.
            text = message.get("text", "") # Get the text of the message, handling cases where it might not exist.

            # --- Core Bot Logic ---
            if text == "/start":
                response_text = "Welcome! I am your simple bot. Type /start to see this message again."
                await send_message(chat_id, response_text)
                print(f"Responded to /start from {chat_id}")
            else:
                # For any other message, tell the user what you understand
                await send_message(chat_id, "I only understand the /start command for now. Try it!")
                print(f"Responded to non-/start message from {chat_id}")
        else:
            print("Received update without a message key (e.g., edited message, channel post, etc.):", update)

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from webhook request: {e}")
    except Exception as e:
        print(f"An unexpected error occurred in webhook: {e}")

    # Always return a 200 OK status to Telegram to confirm successful receipt of the update.
    # If you don't return 200 OK, Telegram might keep retrying the update.
    return {"status": "ok"}

# --- Instructions for Deployment ---
# 1. Save this code as `main.py` in your GitHub repository.
# 2. Ensure your `requirements.txt` file includes:
#    fastapi
#    uvicorn
#    httpx
#    python-dotenv
# 3. In your Render service settings:
#    - Build Command: `pip install -r requirements.txt`
#    - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
#      (Note: Render automatically sets the $PORT environment variable)
#    - Environment Variables: Add `BOT_TOKEN` with your bot's token.
# 4. After Render successfully deploys and your service is "live":
#    - Run your `set_webhook.py` script (which I've provided before) ONCE.
#    - The `WEBHOOK_URL` in `set_webhook.py` must be your Render service's public URL followed by `/webhook`.
#      Example: `https://telegram-bot-quut.onrender.com/webhook`
