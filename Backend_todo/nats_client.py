import os
import json
import asyncio
from nats.aio.client import Client as NATS
from nats.errors import ConnectionClosedError, NoServersError


NATS_URL = os.getenv("NATS_URL", "nats://my-nats:4222")

# Global singleton client
nc = None
nc_lock = asyncio.Lock()  # ensures thread-safe initialization


async def get_nats_connection():
    """
    Create (or reuse) a single NATS connection.
    Thread-safe: backend calls this via run_coroutine_threadsafe().
    """
    global nc

    async with nc_lock:
        if nc is not None and nc.is_connected:
            return nc

        new_nc = NATS()
        try:
            await new_nc.connect(
                servers=[NATS_URL],
                reconnect_time_wait=1,
                max_reconnect_attempts=60,
                connect_timeout=2,
            )
            print("NATS connected from backend")
            nc = new_nc
        except Exception as e:
            print("Backend failed to connect to NATS:", e)
            raise

    return nc


async def publish_event(event_type, todo):
    """
    Publish an event to NATS using the shared async client.
    Called from Flask using run_coroutine_threadsafe().
    """
    client = await get_nats_connection()

    msg = {
        "event": event_type,
        "todo": todo
    }
    data = json.dumps(msg).encode()

    try:
        await client.publish("todo.events", data)
        print("Published event:", msg)
    except ConnectionClosedError:
        print("ERROR: NATS connection was closed")
    except NoServersError:
        print("ERROR: No NATS servers available")
    except Exception as e:
        print("Unexpected error during publish:", e)
