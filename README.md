# 📊 Price Tracker Bot

Track product prices from Trendyol and Amazon. Get Telegram notifications when prices drop.

## 🚀 Features

- 🛍️ Track products from Trendyol and Amazon
- 📉 Get Telegram notifications when prices drop
- 🎯 Set target prices and get alerted
- 📈 View price history charts
- 👤 Personal tracking — each user sees only their own products

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

## ⚙️ Setup

```bash
pip install -r requirements.txt
playwright install chromium
```

Create `.env` file:

```
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

Run the app:

```bash
streamlit run app.py
```

Run the bot:

```bash
python3 bot.py
```
