import os
from pyrogram import Client, filters

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

# Initialize the bot
app = Client("renamer_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Start command
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("Hello! Send me a file, and I'll rename it for you.")

# File renaming
@app.on_message(filters.document | filters.video | filters.audio)
async def rename_file(client, message):
    file = message.document or message.video or message.audio
    await message.reply_text("Send me the new filename (without extension).")

    @app.on_message(filters.text & filters.reply)
    async def get_new_filename(client, msg):
        new_name = msg.text + os.path.splitext(file.file_name)[1]
        file_path = await message.download()
        new_file_path = os.path.join(os.path.dirname(file_path), new_name)
        os.rename(file_path, new_file_path)

        await message.reply_document(new_file_path, caption="Here is your renamed file!")
        os.remove(new_file_path)  # Clean up after sending

app.run()
