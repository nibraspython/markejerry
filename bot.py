import os
import logging
from pyrogram import Client, filters
from pyrogram.types import Message

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
from config import API_ID, API_HASH, BOT_TOKEN

bot = Client("FileRenamerBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply_text("Send me a file to rename.")

@bot.on_message(filters.document | filters.video | filters.audio)
async def file_handler(client, message: Message):
    file = message.document or message.video or message.audio
    await message.reply_text(f"Send me the new name for `{file.file_name}`")
    
    @bot.on_message(filters.text & filters.reply)
    async def rename_file(client, new_message: Message):
        new_name = new_message.text
        file_path = await client.download_media(message)
        new_path = os.path.join(os.path.dirname(file_path), new_name)
        os.rename(file_path, new_path)
        await new_message.reply_document(new_path, caption="Here is your renamed file.")
        os.remove(new_path)

if __name__ == "__main__":
    bot.run()
