import os
import time
import schedule
import requests
from dotenv import load_dotenv
from supabase import create_client
from scrapers import get_price

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def send_telegram(chat_id, message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": message, "parse_mode": "HTML"})

def check_prices():
    print("Fiyatlar kontrol ediliyor...")
    result = supabase.table("products").select("*").execute()
    products = result.data

    for product in products:
        current = get_price(product["url"])
        current_price = current["price"]

        if current_price is None:
            print(f"Fiyat alınamadı: {product['name']}")
            continue

        last_price = product.get("last_price")
        target_price = product.get("target_price")
        chat_id = product.get("chat_id")

        if last_price and current_price < last_price:
            send_telegram(
                chat_id,
                f"📉 <b>Price Drop!</b>\n"
                f"🛍️ {product['name']}\n"
                f"💰 Old: {last_price} TL → New: {current_price} TL\n"
                f"📊 Discount: %{round((last_price - current_price) / last_price * 100)}\n"
                f"🔗 {product['url']}"
            )

        if target_price and current_price <= target_price:
            send_telegram(
                chat_id,
                f"🎯 <b>Target Price Reached!</b>\n"
                f"🛍️ {product['name']}\n"
                f"💰 Price: {current_price} TL\n"
                f"🔗 {product['url']}"
            )

        supabase.table("products").update({"last_price": current_price}).eq("id", product["id"]).execute()
        supabase.table("price_history").insert({
            "chat_id": chat_id,
            "url": product["url"],
            "price": current_price,
            "date": time.strftime("%Y-%m-%d %H:%M")
        }).execute()

        print(f"{product['name']}: {current_price} TL")

if __name__ == "__main__":
    print("🤖 Price Tracker otomatik kontrol başladı!")
    schedule.every(30).minutes.do(check_prices)
    check_prices()

    while True:
        schedule.run_pending()
        time.sleep(60)