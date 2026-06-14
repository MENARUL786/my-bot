import os
import asyncio
import requests
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pyrogram import Client, filters
import google.generativeai as genai
import firebase_admin
from firebase_admin import db

# এনভায়রনমেন্ট ভেরিয়েবল থেকে কনফিগারেশন নেওয়া (নিরাপদ পদ্ধতি)
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
FIREBASE_DB_URL = os.environ.get("FIREBASE_DB_URL")

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

# ওয়েব সার্ভার ক্লাস
class WebServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Menarul Userbot is Online!")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), WebServerHandler)
    server.serve_forever()

@app.on_message(filters.private | filters.group)
async def handle_userbot_logic(client, message):
    # সংক্ষেপে কোর লজিক (আপনার আগের কোড অনুযায়ী)
    if message.text and message.text.startswith(".btc"):
        try:
            res = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd").json()
            await message.reply_text(f"📈 BTC Price: ${res['bitcoin']['usd']:,} USD")
        except: pass
        return

    # জেমিনি রেসপন্স
    if message.chat.type == "private":
        try:
            response = ai_model.generate_content(message.text)
            await message.reply_text(response.text)
        except:
            await message.reply_text("সার্ভার বিজি ভাই!")

async def main():
    await app.start()
    print("🚀 বট সাকসেসফুলি চালু হয়েছে!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()
    try:
        app.run(main())
    except Exception as e:
        print(f"Error: {e}")
    
