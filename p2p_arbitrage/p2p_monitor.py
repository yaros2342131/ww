#!/usr/bin/env python3
"""
P2P монитор USDT/UAH: OKX, Bybit, Telegram Wallet.
Шлёт сообщение в Telegram-бота, когда цена ПОКУПКИ USDT <= MAX_PRICE.

Настройка через переменные окружения (или файл .env рядом со скриптом):
  TG_BOT_TOKEN   токен бота от @BotFather
  TG_CHAT_ID     ваш chat id (узнать у @userinfobot)
  MAX_PRICE      порог, по умолчанию 45.40
  MIN_LIMIT_UAH  (необяз.) минимальный лимит объявления в UAH, чтобы объявление вам подходило по сумме
  INTERVAL       период опроса в секундах, по умолчанию 30
  WALLET_API_KEY (необяз.) ключ Telegram Wallet P2P, если API требует
"""
import os
import time
import logging
import requests

def load_env():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"'))

load_env()
TOKEN = os.environ.get("TG_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TG_CHAT_ID", "")
MAX_PRICE = float(os.environ.get("MAX_PRICE", "45.40"))
MIN_LIMIT = float(os.environ.get("MIN_LIMIT_UAH", "0"))
INTERVAL = int(os.environ.get("INTERVAL", "30"))
WALLET_KEY = os.environ.get("WALLET_API_KEY", "")
REPEAT_AFTER = 600  # не спамить одним и тем же объявлением чаще, чем раз в 10 мин

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36"}
log = logging.getLogger("p2p")


def get_okx():
    """Объявления, где продавцы продают USDT за UAH (вы покупаете)."""
    r = requests.get(
        "https://www.okx.com/v3/c2c/tradingOrders/books",
        params={"quoteCurrency": "UAH", "baseCurrency": "USDT", "side": "sell",
                "paymentMethod": "all", "userType": "all", "showTrade": "false",
                "showFollow": "false", "showAlreadyTraded": "false",
                "isAbleFilter": "false", "t": int(time.time() * 1000)},
        headers=UA, timeout=15)
    r.raise_for_status()
    out = []
    for a in r.json().get("data", {}).get("sell", []):
        out.append(dict(id=a.get("id"), price=float(a["price"]),
                        seller=a.get("nickName"),
                        min=float(a.get("quoteMinAmountPerOrder") or 0),
                        max=float(a.get("quoteMaxAmountPerOrder") or 0),
                        pay=", ".join(a.get("paymentMethods", []))))
    return out


def get_bybit():
    r = requests.post(
        "https://api2.bybit.com/fiat/otc/item/online",
        json={"userId": "", "tokenId": "USDT", "currencyId": "UAH", "payment": [],
              "side": "1", "size": "30", "page": "1", "amount": "",
              "authMaker": False, "canTrade": False},
        headers=UA, timeout=15)
    r.raise_for_status()
    out = []
    for a in (r.json().get("result") or {}).get("items", []):
        out.append(dict(id=a.get("id"), price=float(a["price"]),
                        seller=a.get("nickName"),
                        min=float(a.get("minAmount") or 0),
                        max=float(a.get("maxAmount") or 0),
                        pay=""))
    return out


def get_wallet():
    """Telegram Wallet P2P. Формат ответа может отличаться — парсер терпимый.
    Если получаете ошибку 401/403 — задайте WALLET_API_KEY."""
    headers = dict(UA)
    if WALLET_KEY:
        headers["Wallet-Api-Key"] = WALLET_KEY
    r = requests.post(
        "https://p2p.walletbot.me/p2p/integration-api/v1/item/online",
        json={"baseCurrencyCode": "USDT", "quoteCurrencyCode": "UAH",
              "offerType": "SALE", "offset": 0, "limit": 50},
        headers=headers, timeout=15)
    r.raise_for_status()
    data = r.json().get("data") or []
    out = []
    for a in data:
        p = a.get("price")
        p = p.get("value") if isinstance(p, dict) else p
        if p is None:
            continue
        lim = a.get("orderAmountLimits") or {}
        out.append(dict(id=a.get("id"), price=float(p),
                        seller=(a.get("user") or {}).get("nickname"),
                        min=float(lim.get("min") or 0),
                        max=float(lim.get("max") or 0), pay=""))
    return out


SOURCES = {"OKX": get_okx, "Bybit": get_bybit, "Telegram Wallet": get_wallet}


def send(text):
    r = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                      json={"chat_id": CHAT_ID, "text": text,
                            "parse_mode": "HTML"}, timeout=15)
    if not r.ok:
        log.error("Telegram: %s %s", r.status_code, r.text)


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    if not TOKEN or not CHAT_ID:
        raise SystemExit("Задайте TG_BOT_TOKEN и TG_CHAT_ID (см. .env.example)")
    sent = {}
    send(f"✅ Монитор запущен. Ищу USDT ≤ {MAX_PRICE} UAH (OKX, Bybit, Wallet)")
    while True:
        for name, fn in SOURCES.items():
            try:
                ads = fn()
            except Exception as e:
                log.warning("%s: ошибка %s", name, e)
                continue
            if not ads:
                continue
            log.info("%s: лучшая цена %.2f (%d объявл.)", name,
                     min(a["price"] for a in ads), len(ads))
            for a in sorted(ads, key=lambda x: x["price"]):
                if a["price"] > MAX_PRICE:
                    break
                if MIN_LIMIT and a["max"] and a["max"] < MIN_LIMIT:
                    continue
                key = (name, a["id"], a["price"])
                if time.time() - sent.get(key, 0) < REPEAT_AFTER:
                    continue
                sent[key] = time.time()
                send(f"💰 <b>{name}</b>: купить USDT по <b>{a['price']:.2f}</b> UAH\n"
                     f"Продавец: {a['seller']}\n"
                     f"Лимиты: {a['min']:.0f}–{a['max']:.0f} UAH\n"
                     f"{a['pay']}".strip())
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
