import plotly.express as px
import pandas as pd
from datetime import datetime
import streamlit as st
import os
from dotenv import load_dotenv
from scrapers import get_price
import requests
from supabase import create_client

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(
    page_title="Price Tracker",
    page_icon="📊",
    layout="wide"
)

def send_telegram(chat_id, message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": message, "parse_mode": "HTML"})

def get_user_products(chat_id):
    result = supabase.table("products").select("*").eq("chat_id", str(chat_id)).execute()
    return result.data

def add_user_product(chat_id, url, name, target_price, last_price, image):
    supabase.table("products").insert({
        "chat_id": str(chat_id),
        "url": url,
        "name": name,
        "target_price": target_price,
        "last_price": last_price,
        "image": image
    }).execute()

def update_product_price(chat_id, url, new_price):
    supabase.table("products").update({"last_price": new_price}).eq("chat_id", str(chat_id)).eq("url", url).execute()

def delete_user_product(chat_id, url):
    supabase.table("products").delete().eq("chat_id", str(chat_id)).eq("url", url).execute()

def delete_all_products(chat_id):
    supabase.table("products").delete().eq("chat_id", str(chat_id)).execute()

def add_price_history(chat_id, url, price):
    supabase.table("price_history").insert({
        "chat_id": str(chat_id),
        "url": url,
        "price": price,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }).execute()

def get_price_history(chat_id, url):
    result = supabase.table("price_history").select("*").eq("chat_id", str(chat_id)).eq("url", url).execute()
    return result.data

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
                        add_user_product(chat_id, url, name, target_price, result["price"], result["image"])
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
            delete_all_products(chat_id)
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
                        
                        update_product_price(chat_id, product["url"], current_price)
                        add_price_history(chat_id, product["url"], current_price)
                
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
                    delete_user_product(chat_id, product["url"])
                    st.rerun()
            
            history = get_price_history(chat_id, product["url"])
            if len(history) >= 2:
                df = pd.DataFrame(history)
                fig = px.line(df, x="date", y="price",
                            title=f"📈 {product['name']} Price History",
                            labels={"date": "Date", "price": "Price (TL)"})
                fig.update_layout(height=250, margin=dict(l=0, r=0, t=40, b=0))
                st.plotly_chart(fig, use_container_width=True)
            
            st.divider()