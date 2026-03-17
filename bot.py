import os
from dotenv import load_dotenv
import requests
import time

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")

def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    params = {"timeout": 30}
    if offset:
        params["offset"] = offset
    response = requests.get(url, params=params)
    return response.json()

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": text, "parse_mode": "HTML"})

def run_bot():
    print("🤖 Bot başladı!")
    offset = None
    
    while True:
        try:
            updates = get_updates(offset)
            
            for update in updates.get("result", []):
                offset = update["update_id"] + 1
                
                message = update.get("message", {})
                chat_id = message.get("chat", {}).get("id")
                text = message.get("text", "")
                
                if text == "/start":
                    send_message(chat_id, 
                        f"👋 Welcome to Price Tracker Bot!\n\n"
                        f"Your Chat ID is: <b>{chat_id}</b>\n\n"
                        f"Copy this ID and paste it into the app to start tracking prices!"
                    )
                
                elif text == "/myid":
                    send_message(chat_id,
                        f"🆔 Your Chat ID: <b>{chat_id}</b>"
                    )
        
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_bot()