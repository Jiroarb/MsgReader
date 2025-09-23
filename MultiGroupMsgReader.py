import logging
import yaml
import requests
from telethon import TelegramClient, events

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)

# === Load config ===
config_path = "/etc/secrets/config.yaml"

with open(config_path, "r") as f:
    config = yaml.safe_load(f)

api_id = int(config["telegram"]["api_id"])
api_hash = config["telegram"]["api_hash"]
phone = config["telegram"]["phone"]

client = TelegramClient("my_account", api_id, api_hash)

# Prepare routes
routes = {r["source"]: r for r in config["routes"]}

logger.info("Listening for messages...")

# === Event handler (per group) ===
@client.on(events.NewMessage(chats=list(routes.keys())))
async def handler(event):
    logger.info("Inside Listening for messages...")
    msg = event.text or "📎 Media received"
    source = event.chat.username or event.chat.title
    print(f"[{source}] {msg}")
    logger.info(f"New message in {chat_id}: {msg}")

    route = routes.get(f"https://t.me/{event.chat.username}", None)
    if not route:
        return

    # --- Forward to Signal ---
    if "signal" in route:
        payload = {
            "message": msg,
            "number": route["signal"]["number"],
            "recipients": route["signal"]["recipients"],
        }
        try:
            r = requests.post("http://localhost:8080/v2/send", json=payload)
            print("Signal response:", r.text)
            logger.error(f"Signal response:{r.text}")
        except Exception as e:
            print("Signal error:", e)
            logger.error(f"Signal error: {e}")

    # --- Forward to Telegram channels ---
    if "telegram_channels" in route:
        for chan in route["telegram_channels"]:
            try:
                await client.send_message(chan, f"[{source}] {msg}")
                print(f"Forwarded to {chan}")
                logger.info(f"Forwarded to Telegram {chan}")
            except Exception as e:
                print("Telegram forward error:", e)                
                logger.error(f"Telegram forward error:{e}")

# === Run client ===
with client:
    print("Starting python")
    client.run_until_disconnected()
