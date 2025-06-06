from flask import Flask
import requests
from datetime import datetime

app = Flask(__name__)

TELEGRAM_TOKEN = "8039064596:AAF2avPda5L_SQw8fqCMO6qquoCBYmtA_C4"
CHAT_ID = "197984048"

COINS = {
    "bitcoin": {"symbol": "BTC"},
    "binancecoin": {"symbol": "BNB"},
}

def get_price(coin_id):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=eur"
    return requests.get(url).json()[coin_id]["eur"]

def get_ath_eur(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    data = requests.get(url).json()
    ath_usd = data["market_data"]["ath"]["usd"]
    fx_url = "https://api.exchangerate.host/latest?base=USD&symbols=EUR"
    fx_rate = requests.get(fx_url).json()["rates"]["EUR"]
    return ath_usd * fx_rate

def determine_investment(price, ath):
    ratio = price / ath * 100
    if ratio <= 55: return 200
    elif ratio <= 65: return 125
    elif ratio <= 75: return 100
    elif ratio <= 85: return 75
    elif ratio <= 95: return 50
    elif ratio <= 100: return 25
    else: return 0

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, data=payload)

def main():
    now = datetime.now().strftime("%A %d %B %Y")
    message = f"*📊 Rapport Hebdo - {now}*\n\n"
    for coin_id, info in COINS.items():
        current = get_price(coin_id)
        ath = get_ath_eur(coin_id)
        gap = 100 - (current / ath * 100)
        invest = determine_investment(current, ath)
        message += (
            f"*{info['symbol']}* :\n"
            f"- Prix actuel : {current:.2f} €\n"
            f"- ATH : {ath:.2f} €\n"
            f"- Écart : {gap:.2f}% ⬇️\n"
            f"- 💸 Achat recommandé : *{invest} €*\n\n"
        )
    send_telegram_message(message)

@app.route("/")
def index():
    return "Bot DCA actif"

@app.route("/run")
def run():
    main()
    return "Message envoyé"

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
