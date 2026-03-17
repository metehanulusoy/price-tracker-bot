import os
import json
import schedule
import time
import requests
from dotenv import load_dotenv
from scrapers import get_price

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DATA_FILE = "products.json"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"})

def load_products():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_products(products):
    with open(DATA_FILE, "w") as f:
        json.dump(products, f, indent=2, ensure_ascii=False)

def add_product(url, name, target_price):
    products = load_products()
    current_price = get_price(url)
    products.append({
        "url": url,
        "name": name,
        "target_price": target_price,
        "last_price": current_price
    })
    save_products(products)
    send_telegram(f"✅ <b>{name}</b> takibe alındı!\n💰 Şu anki fiyat: {current_price} TL\n🎯 Hedef fiyat: {target_price} TL")
    print(f"Ürün eklendi: {name} - {current_price} TL")

def check_prices():
    products = load_products()
    updated = False
    
    for product in products:
        current_price = get_price(product["url"])
        
        if current_price is None:
            print(f"Fiyat alınamadı: {product['name']}")
            continue
        
        last_price = product.get("last_price")
        target_price = product.get("target_price")
        
        # Fiyat düştü mü?
        if last_price and current_price < last_price:
            send_telegram(
                f"📉 <b>Fiyat Düştü!</b>\n"
                f"🛍️ {product['name']}\n"
                f"💰 Eski fiyat: {last_price} TL\n"
                f"💸 Yeni fiyat: {current_price} TL\n"
                f"📊 İndirim: %{round((last_price - current_price) / last_price * 100)}\n"
                f"🔗 {product['url']}"
            )
        
        # Hedef fiyata ulaştı mı?
        if target_price and current_price <= target_price:
            send_telegram(
                f"🎯 <b>Hedef Fiyata Ulaşıldı!</b>\n"
                f"🛍️ {product['name']}\n"
                f"💰 Fiyat: {current_price} TL\n"
                f"🎯 Hedef: {target_price} TL\n"
                f"🔗 {product['url']}"
            )
        
        product["last_price"] = current_price
        updated = True
        print(f"{product['name']}: {current_price} TL")
    
    if updated:
        save_products(products)

if __name__ == "__main__":
    print("🤖 Price Tracker Bot başladı!")
    send_telegram("🤖 <b>Price Tracker Bot aktif!</b>\nFiyatlar her 30 dakikada kontrol edilecek.")
    
    # Örnek ürün ekle (test için)
    # add_product("https://www.trendyol.com/...", "Ürün Adı", 500)
    
    # Her 30 dakikada fiyat kontrol et
    schedule.every(30).minutes.do(check_prices)
    
    # İlk kontrolü hemen yap
    check_prices()
    
    while True:
        schedule.run_pending()
        time.sleep(60)