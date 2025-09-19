import yaml
import requests
from telethon import TelegramClient, events

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

# === Event handler (per group) ===
@client.on(events.NewMessage(chats=list(routes.keys())))
async def handler(event):
    msg = event.text or "📎 Media received"
    source = event.chat.username or event.chat.title
    print(f"[{source}] {msg}")

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
        except Exception as e:
            print("Signal error:", e)

    # --- Forward to Telegram channels ---
    if "telegram_channels" in route:
        for chan in route["telegram_channels"]:
            try:
                await client.send_message(chan, f"[{source}] {msg}")
                print(f"Forwarded to {chan}")
            except Exception as e:
                print("Telegram forward error:", e)


# === Run client ===
with client:
    print("Starting python")
    client.run_until_disconnected()
