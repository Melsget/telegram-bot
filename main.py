import os
import httpx
import asyncio
import json # Import json for pretty printing
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set in .env")

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

async def get_webhook_info():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_URL}/getWebhookInfo")
            response.raise_for_status()
            # Print with indentation for readability
            print("Webhook Info:", json.dumps(response.json(), indent=2))
    except httpx.RequestError as e:
        print(f"Error fetching webhook info: {e}")
    except httpx.HTTPStatusError as e:
        print(f"Error response {e.response.status_code} while fetching webhook info: {e.response.text}")

if __name__ == "__main__":
    asyncio.run(get_webhook_info())
