import os # Used for interacting with the operating system, specifically to access environment variables.
import httpx # An asynchronous HTTP client library used to make requests to the Telegram Bot API.
import asyncio # Python's built-in library for writing concurrent code using the async/await syntax.
import json # Used for working with JSON data, which is the format Telegram uses for updates and responses.
from dotenv import load_dotenv # A library to load environment variables from a .env file.
from fastapi import FastAPI, Request # FastAPI is a web framework for building APIs. Request is used to access incoming request data.

# --- Configuration and Initialization ---

load_dotenv() # This function loads all environment variables from the .env file into os.environ.

# Retrieve the bot token from environment variables.
# It's crucial to store sensitive information like tokens outside the code itself for security.
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Raise an error if the BOT_TOKEN is not found, as the bot cannot function without it.
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set. Please get your token from BotFather and add it to a .env file.")

# Construct the base URL for the Telegram Bot API. All API requests will start with this.
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Initialize the FastAPI application. This 'app' object will define our web endpoints.
app = FastAPI()

# --- Telegram API Interaction Functions ---

async def send_message(chat_id: int, text: str):
    """
    Asynchronously sends a message to a specified chat ID on Telegram.
    :param chat_id: The unique identifier for the target chat or user.
    :param text: The text of the message to be sent.
    """
    # Define the payload (data) to be sent in the POST request body.
    # Telegram's sendMessage method requires 'chat_id' and 'text'.
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    try:
        # Create an asynchronous HTTP client session. 'async with' ensures the client is properly closed.
        async with httpx.AsyncClient() as client:
            # Send a POST request to the sendMessage API endpoint.
            # The 'json=payload' argument automatically serializes the dictionary to JSON and sets the Content-Type header.
            response = await client.post(f"{API_URL}/sendMessage", json=payload)
            # Check if the HTTP request was successful (status code 2xx).
            response.raise_for_status()
            # Log success message (optional, but good for debugging).
            print(f"Message sent to {chat_id}: {text}")
    except httpx.RequestError as e:
        # Catch network-related errors (e.g., DNS resolution failure, connection refused).
        print(f"Error sending message (request error): {e}")
    except httpx.HTTPStatusError as e:
        # Catch HTTP status errors (e.g., 404, 500 from Telegram API).
        print(f"Error response {e.response.status_code} while sending message: {e.response.text}")

# --- FastAPI Webhook Endpoints ---

@app.get("/")
async def health_check():
    """
    A simple GET endpoint to check if the bot server is running.
    This is useful for deployment platforms like Render to confirm your service is healthy.
    """
    return {"status": "ok", "message": "Bot server is running!"}

@app.post("/webhook")
async def telegram_webhook(request: Request):
    """
    This is the main endpoint where Telegram will send updates (messages, callbacks, etc.)
    when a webhook is configured.
    :param request: The incoming FastAPI Request object, containing the raw HTTP request.
    """
    # Parse the incoming request body as JSON.
    # Telegram sends updates as JSON.
    update = await request.json()
    print(f"Received Telegram update: {json.dumps(update, indent=2)}") # Log the full update for debugging

    # Check if the update contains a 'message' field.
    # Not all updates are messages (e.g., callback queries, channel posts).
    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"] # Extract the ID of the chat where the message originated.
        text = message.get("text", "") # Extract the text of the message, defaulting to an empty string if no text (e.g., sticker).

        # Check if the received text is the '/start' command.
        if text == "/start":
            # If it's '/start', send a specific welcome message.
            await send_message(chat_id, "Hello! I am your simple Telegram bot. How can I help you?")
            print(f"Responded to /start from {chat_id}")
        else:
            # For any other text message, you could echo it back or send a different response.
            await send_message(chat_id, f"You sent: '{text}'. Try sending /start to get a welcome message!")
            print(f"Responded to non-/start message from {chat_id}")

    # It's good practice to return a 200 OK status to Telegram to confirm receipt of the update.
    return {"status": "ok"}

# --- How to Run This Bot ---
# 1. Save this code as `main.py` (or `my_first_bot.py`).
# 2. Create a `.env` file in the same directory with `BOT_TOKEN="YOUR_BOT_TOKEN_HERE"`.
# 3. Install necessary libraries: `pip install fastapi uvicorn httpx python-dotenv`.
# 4. To run locally (for testing webhooks, you'd still need a public URL like ngrok):
#    `uvicorn main:app --reload` (replace `main` with your file name if different)
# 5. For deployment (e.g., on Render):
#    The `Start Command` for Render would be: `uvicorn main:app --host 0.0.0.0 --port $PORT`
#    And remember to set the webhook using a separate script after deployment.
