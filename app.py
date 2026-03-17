import plotly.express as px
import pandas as pd
from datetime import datetime
import streamlit as st
import json
import os
from dotenv import load_dotenv
from scrapers import get_price
import requests

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
DATA_FILE = "products.json"
HISTORY_FILE = "price_history.json"

st.set_page_config(
    page_title="Price Tracker",
    page_icon="📊",
    layout="wide"
)

def send_telegram(chat_id, message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": message, "parse_mode": "HTML"})

def load_all_products():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_all_products(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_user_products(chat_id):
    all_data = load_all_products()
    return all_data.get(str(chat_id), [])

def save_user_products(chat_id, products):
    all_data = load_all_products()
    all_data[str(chat_id)] = products
    save_all_products(all_data)

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def add_price_history(chat_id, product_url, price):
    history = load_history()
    key = f"{chat_id}_{product_url}"
    if key not in history:
        history[key] = []
    history[key].append({
        "price": price,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    save_history(history)

def get_price_history(chat_id, product_url):
    history = load_history()
    key = f"{chat_id}_{product_url}"
    return history.get(key, [])

st.title("📊 Price Tracker")
st.markdown("Track product prices from Trendyol and Amazon. Get Telegram notifications when prices drop.")
st.info("✅ Supported: Trendyol, Amazon.com.tr")
st.divider()

with st.sidebar:
    st.header("🔐 Your Telegram")
    st.markdown("1. Open Telegram\n2. Search `@price_tracker_metehan_bot`\n3. Press Start\n4. Send `/myid`\n5. Enter your Chat ID below")
    
    chat_id = st.text_input("Your Telegram Chat ID")
    
    if chat_id:
        st.success(f"✅ Logged in as {chat_id}")
        st.divider()
        
        st.header("➕ Add Product")
        url = st.text_input("Product URL")
        name = st.text_input("Product Name")
        target_price = st.number_input("Target Price (TL)", min_value=0.0, step=10.0)
        
        if st.button("🔍 Check Price", use_container_width=True):
            if url:
                with st.spinner("Fetching price..."):
                    result = get_price(url)
                if result["price"]:
                    st.success(f"Current price: {result['price']} TL")
                    if result["image"]:
                        st.image(result["image"], width=200)
                else:
                    st.error("Could not fetch price. Check the URL.")
        
        if st.button("✅ Add to Tracker", use_container_width=True):
            if url and name:
                user_products = get_user_products(chat_id)
                if any(p["url"] == url for p in user_products):
                    st.warning("⚠️ This product is already being tracked!")
                else:
                    with st.spinner("Adding product..."):
                        result = get_price(url)
                        user_products.append({
                            "url": url,
                            "name": name,
                            "target_price": target_price,
                            "last_price": result["price"],
                            "image": result["image"]
                        })
                        save_user_products(chat_id, user_products)
                        add_price_history(chat_id, url, result["price"])
                        send_telegram(
                            chat_id,
                            f"✅ <b>{name}</b> is now being tracked!\n"
                            f"💰 Current price: {result['price']} TL\n"
                            f"🎯 Target price: {target_price} TL"
                        )
                    st.success(f"✅ {name} added!")
            else:
                st.warning("Please fill in URL and product name.")
        
        if st.button("🗑️ Clear All", use_container_width=True):
            save_user_products(chat_id, [])
            st.rerun()

if not chat_id:
    st.info("👈 Enter your Telegram Chat ID from the left panel to get started.")
else:
    user_products = get_user_products(chat_id)
    
    if not user_products:
        st.info("👈 Add a product from the left panel to start tracking.")
    else:
        st.markdown(f"### 🛍️ Your Tracked Products ({len(user_products)})")
        
        if st.button("🔄 Refresh All Prices"):
            with st.spinner("Checking all prices..."):
                for product in user_products:
                    result = get_price(product["url"])
                    current_price = result["price"]
                    
                    if current_price:
                        last_price = product.get("last_price")
                        target_price = product.get("target_price")
                        
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
                        
                        product["last_price"] = current_price
                        if result["image"]:
                            product["image"] = result["image"]
                        
                        add_price_history(chat_id, product["url"], current_price)
                
                save_user_products(chat_id, user_products)
            st.success("✅ All prices updated!")
            st.rerun()
        
        st.divider()
        
        for i, product in enumerate(user_products):
            col1, col2, col3, col4, col5 = st.columns([1, 3, 2, 2, 1])
            
            with col1:
                if product.get("image"):
                    st.image(product["image"], width=80)
            with col2:
                st.markdown(f"**{product['name']}**")
                st.caption(product['url'][:50] + "...")
            with col3:
                price = product.get("last_price")
                if price:
                    st.metric("Current Price", f"{price} TL")
                else:
                    st.metric("Current Price", "N/A")
            with col4:
                target = product.get("target_price")
                if target and price:
                    diff = price - target
                    if diff <= 0:
                        st.success("🎯 Target reached!")
                    else:
                        st.metric("Target Price", f"{target} TL", delta=f"-{diff:.0f} TL to go")
            with col5:
                if st.button("🗑️", key=f"del_{i}"):
                    user_products.pop(i)
                    save_user_products(chat_id, user_products)
                    st.rerun()
            
            # Fiyat grafiği
            history = get_price_history(chat_id, product["url"])
            if len(history) >= 2:
                df = pd.DataFrame(history)
                fig = px.line(df, x="date", y="price", 
                            title=f"📈 {product['name']} Price History",
                            labels={"date": "Date", "price": "Price (TL)"})
                fig.update_layout(height=250, margin=dict(l=0, r=0, t=40, b=0))
                st.plotly_chart(fig, use_container_width=True)
            
            st.divider()