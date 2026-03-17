# 📊 Price Tracker Bot

Track product prices from Trendyol and Amazon. Get Telegram notifications when prices drop.

## ✨ Features
- 🛍️ Track products from Trendyol and Amazon
- 📉 Get Telegram notifications when prices drop
- 🎯 Set target prices and get alerted
- 📈 View price history charts
- 👤 Personal tracking per user
- 💾 Persistent storage with Supabase

## 📱 How to Use
1. Open Telegram
2. Search `@price_tracker_metehan_bot`
3. Press Start and send `/myid`
4. Copy your Chat ID
5. Paste it into the app
6. Add products and start tracking!

## 🛠️ Tech Stack
- Python
- Playwright (web scraping)
- Streamlit (UI)
- Plotly (charts)
- Telegram Bot API
- Supabase (database)

## ⚙️ Requirements
- Python 3.10+
- Supabase account (free tier works)
- Telegram Bot Token (from @BotFather)
- OpenAI API key (not required for this project)

## 🚀 Setup

**1. Install dependencies:**
```bash
pip install -r requirements.txt
playwright install chromium
```

**2. Create `.env` file:**
```
TELEGRAM_TOKEN=your_telegram_bot_token
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_secret_key
```

**3. Create Supabase tables:**

`products` table:
- id (int8, primary key)
- chat_id (text)
- url (text)
- name (text)
- target_price (float8)
- last_price (float8)
- image (text)

`price_history` table:
- id (int8, primary key)
- chat_id (text)
- url (text)
- price (float8)
- date (text)

**4. Run the web app:**
```bash
streamlit run app.py
```

**5. Run the Telegram bot (to get Chat IDs):**
```bash
python3 bot.py
```

**6. Run automatic price checker (optional, keep terminal open):**
```bash
python3 main.py
```
> ⚠️ main.py checks prices every 30 minutes and sends Telegram notifications. Keep it running for automatic alerts.

## ⚠️ Notes
- Automatic price notifications only work while `main.py` is running
- For 24/7 notifications, deploy `main.py` to a server (Railway, Render, etc.)
- Supported sites: Trendyol, Amazon.com.tr