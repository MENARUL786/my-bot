import os
import asyncio
import re
import time
from datetime import datetime
import requests
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
import google.generativeai as genai
import firebase_admin
from firebase_admin import credentials, db
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# আপনার ক্রেডেনশিয়ালস (সরাসরি কোডে বসানো হলো)
API_ID = 26244621
API_HASH = "7655847a00a1d5d266fb262beadeeccd"
SESSION_STRING = "AQ.Ab8RN6JQqWSHWja5p2J6ri1YocOJ_QL8cA5Xwqmz4fE4-N2GRw"
GEMINI_API_KEY = "AIzaSyDHoZMiw_ULPMy1vjwHafhQ4UlEcP3woQU" 
FIREBASE_DB_URL = "https://menerul-panel-2026-default-rtdb.firebaseio.com"

# ইনিশিয়ালাইজেশন
genai.configure(api_key=GEMINI_API_KEY)
ai_model = genai.GenerativeModel('gemini-pro')

if not firebase_admin._apps:
    options = {'databaseURL': FIREBASE_DB_URL}
    firebase_admin.initialize_app(options=options)

app = Client(
    "Menerul_Userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

chat_memory = {}

# ডাটাবেজ সেটিংস
def get_panel_settings():
    try:
        ref = db.reference('/')
        return ref.get() or {}
    except: return {}

# কোর লজিক
@app.on_message(filters.private | filters.group)
async def handle_userbot_logic(client, message):
    data = get_panel_settings()
    settings = data.get('settings', {})
    if not data.get('bot_status', True): return
    user_id = str(message.from_user.id) if message.from_user else None
    if not user_id or data.get('blacklist', {}).get(user_id): return
    
    if message.chat.type == "private":
        text_msg = message.text.strip().lower() if message.text else ""
        
        if text_msg in [".btc", ".eth"] and settings.get('crypto_check'):
            coin = "bitcoin" if text_msg == ".btc" else "ethereum"
            try:
                res = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd").json()
                await message.reply_text(f"📈 **{coin.upper()}:** ${res[coin]['usd']:,} USD")
            except: pass
            return

        try:
            response = ai_model.generate_content(message.text)
            await message.reply_text(response.text)
        except: await message.reply_text("সার্ভার বিজি ভাই!")

# ওয়েব সার্ভার (রেন্ডার চালু রাখার জন্য)
class WebServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Menarul Userbot is Online!")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), WebServerHandler)
    server.serve_forever()

if __name__ == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()
    print("🚀 বট সার্ভার চালু হচ্ছে...")
    app.run()
    
