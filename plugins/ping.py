from pyrogram import Client, filters
import time

@Client.on_message(filters.command("ping"))
async def ping_pong(client, message):
    start_time = time.time()
    reply = await message.reply_text("Pinging... ⏳")
    end_time = time.time()
    
    latency = round((end_time - start_time) * 1000, 2)  # Convert to milliseconds
    await reply.edit_text(f"Pong! ⚡️\n⏱️ `{latency} ms`")
