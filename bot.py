import time
import requests
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

TG_BASE = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
CG_BASE = "https://api.coingecko.com/api/v3"

CHANNEL_ID = https://t.me/+mKGP2vJamQhkNGMy
ADMIN_IDS = [@Kaka_FTBL]

INTERVAL = 60
WINDOW = 3

monitor_mode = None

price_history = {}
sent_alerts = set()

# 🐸 STICKER ID-lər (istəsən dəyişə bilərsən)
PUMP_STICKER = "CAACAgIAAxkBAAIBQmPeFqFhFrog"  
DUMP_STICKER = "CAACAgIAAxkBAAIBR2PeFqKexample"

def send_message(chat_id, text):
    requests.post(f"{TG_BASE}/sendMessage", data={
        "chat_id": chat_id,
        "text": text
    })

def send_sticker(chat_id, sticker):
    requests.post(f"{TG_BASE}/sendSticker", data={
        "chat_id": chat_id,
        "sticker": sticker
    })

def get_coins():
    url = f"{CG_BASE}/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "volume_desc",
        "per_page": 50,
        "page": 1
    }
    try:
        return requests.get(url, params=params).json()
    except:
        return []

def check_market():
    global price_history, sent_alerts

    coins = get_coins()
    now = time.time()

    for coin in coins:
        symbol = coin["symbol"]
        name = coin["name"]
        price = coin["current_price"]

        if symbol not in price_history:
            price_history[symbol] = []

        price_history[symbol].append((now, price))

        price_history[symbol] = [
            (t, p) for t, p in price_history[symbol]
            if now - t <= WINDOW * 60
        ]

        if len(price_history[symbol]) < 2:
            continue

        old_price = price_history[symbol][0][1]

        if old_price == 0:
            continue

        change = ((price - old_price) / old_price) * 100

        key = f"{symbol}_{int(change)}"

        if change >= 3 and key not in sent_alerts:
            send_sticker(CHANNEL_ID, PUMP_STICKER)
            send_message(CHANNEL_ID,
                f"🚀 PUMP ALERT\n{name} ({symbol.upper()})\n+{change:.2f}% (son 3 dəqiqə)"
            )
            sent_alerts.add(key)

        elif change <= -3 and key not in sent_alerts:
            send_sticker(CHANNEL_ID, DUMP_STICKER)
            send_message(CHANNEL_ID,
                f"🔴 DUMP ALERT\n{name} ({symbol.upper()})\n{change:.2f}% (son 3 dəqiqə)"
            )
            sent_alerts.add(key)

def get_updates(offset=None):
    url = f"{TG_BASE}/getUpdates"
    params = {"timeout": 100}
    if offset:
        params["offset"] = offset
    return requests.get(url, params=params).json()

def handle_commands(text, user_id):
    global monitor_mode

    if user_id not in ADMIN_IDS:
        return

    if text == "/startmeme":
        monitor_mode = "meme"
        send_message(CHANNEL_ID, "🐸 Meme monitor başladı")

    elif text == "/startbirja":
        monitor_mode = "birja"
        send_message(CHANNEL_ID, "📊 Birja monitor başladı")

    elif text == "/startnewcoin":
        monitor_mode = "new"
        send_message(CHANNEL_ID, "🆕 New coin monitor başladı")

    elif text == "/stop":
        monitor_mode = None
        send_message(CHANNEL_ID, "⛔ Monitor dayandı")

def main():
    offset = None

    while True:
        try:
            updates = get_updates(offset)

            for update in updates.get("result", []):
                offset = update["update_id"] + 1

                if "message" in update:
                    msg = update["message"]
                    text = msg.get("text", "")
                    user_id = msg["from"]["id"]

                    handle_commands(text, user_id)

            if monitor_mode:
                check_market()

        except Exception as e:
            print("Error:", e)

        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
