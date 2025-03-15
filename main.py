import os
import logging
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import Message

# Load environment variables
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# Initialize Flask for Render & UptimeRobot
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running!"

# Initialize Pyrogram bot
bot = Client("file_renamer_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Send "I'm alive" message on startup
@bot.on_message(filters.command("start") & filters.user(ADMIN_ID))
def start(_, message: Message):
    message.reply_text("✅ Bot is running and ready to rename files!")

# Handle file uploads
@bot.on_message(filters.document | filters.video | filters.audio)
def file_received(client, message: Message):
    message.reply_text("📌 Send me the new filename (without extension).")
    bot.set_parse_mode("Markdown")
    bot.set_chat_action(message.chat.id, "typing")
    client.listen(message.chat.id, rename_file, filters.text & filters.user(message.from_user.id), timeout=60)

# Rename and send the file
async def rename_file(client, message: Message):
    new_filename = message.text.strip()
    if not new_filename:
        await message.reply_text("❌ Filename cannot be empty!")
        return
    
    received_file = message.reply_to_message.document or message.reply_to_message.video or message.reply_to_message.audio
    file_ext = os.path.splitext(received_file.file_name)[1]
    new_file_name = f"{new_filename}{file_ext}"
    
    sent_msg = await message.reply_text("🔄 Renaming file...")
    downloaded_path = await client.download_media(received_file)
    os.rename(downloaded_path, new_file_name)
    
    await client.send_document(
        chat_id=message.chat.id,
        document=new_file_name,
        caption=f"✅ File renamed to: {new_file_name}"
    )
    
    await sent_msg.delete()
    os.remove(new_file_name)

if __name__ == "__main__":
    bot.start()
    app.run(host="0.0.0.0", port=8080)
