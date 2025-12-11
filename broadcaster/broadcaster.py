import os
import json
import asyncio
import aiohttp
from nats.aio.client import Client as NATS

NATS_URL = os.getenv("NATS_URL", "nats://my-nats:4222")
WEBHOOK_URL = os.getenv("WEBHOOK_URL") 
BROADCAST_MODE = os.getenv("BROADCAST_MODE", "normal")

async def send_to_webhook(message: dict):
    """Send formatted message to external service"""

    if BROADCAST_MODE == "log_only":
        print("[STAGING] LOG-ONLY MODE:", message)
        return

    if not WEBHOOK_URL:
        print("WEBHOOK_URL is not set")
        return

    async with aiohttp.ClientSession() as session:
        try:
            payload = {
                "user": "todo-bot",
                "message": f"[{message['event']}] {message['content']} (id={message['id']}, done={message['done']})"
            }
            async with session.post(WEBHOOK_URL, json=payload) as resp:
                print(f"Webhook status: {resp.status}")
        except Exception as e:
            print("Failed to send webhook:", e)


async def main():
    nc = NATS()

    print("Connecting to NATS...")
    await nc.connect(
    servers=[NATS_URL],
    connect_timeout=2,
    reconnect_time_wait=1,
    max_reconnect_attempts=60,
    )

    print("Broadcaster connected. Listening...")

    # QUEUE GROUP: ensures only ONE broadcast per event (even with many replicas)
    async def message_handler(msg):
        try:
            data = json.loads(msg.data.decode())
            print("Received event:", data)
            todo = data["todo"] 
            formatted = {
                "event": data["event"],
                "id": todo["id"],
                "content": todo["content"],
                "done": todo["done"]
            }
            print("Parsed event:", formatted)
            await send_to_webhook(formatted)
        except Exception as e:
            print("Failed to process message:", e)

    await nc.subscribe(
        "todo.events",
        queue="broadcaster.workers", 
        cb=message_handler
    )

    # keep alive forever
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
