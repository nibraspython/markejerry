from pyrogram import Client, filters
import os
import shutil
from flask import Flask
import threading

# Bot Configuration
API_ID = "your_api_id"
API_HASH = "your_api_hash"
BOT_TOKEN = "your_bot_token"
ADMIN_ID = "6292143807" # Replace with your Telegram ID

# Initialize bot
app = Client("renamer_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Flask Web Server (Keeps Render Alive)
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Bot is running!"

def run_web():
    web_app.run(host='0.0.0.0', port=8080)

# Send Alive Message to Admin
@app.on_message(filters.command("start"))
def start(client, message):
    message.reply_text("Send me a file to rename.")
    if message.from_user.id == ADMIN_ID:
        client.send_message(ADMIN_ID, "✅ Bot is Online and Running!")

@app.on_message(filters.document | filters.video | filters.audio)
def get_new_filename(client, message):
    try:
        file_path = app.download_media(message)
        if not file_path:
            message.reply_text("❌ Failed to download the file.")
            return
        
        new_name = "renamed_" + os.path.basename(file_path)
        new_path = os.path.join(os.path.dirname(file_path), new_name)
        
        if os.path.exists(file_path):
            os.rename(file_path, new_path)
            message.reply_document(new_path, caption="✅ File Renamed Successfully!")
            os.remove(new_path)
        else:
            message.reply_text("❌ File not found after download. Try again.")
    except Exception as e:
        message.reply_text(f"❌ Error: {str(e)}")

# Start Flask in a separate thread
t = threading.Thread(target=run_web)
t.start()

# Run the bot
app.run()
