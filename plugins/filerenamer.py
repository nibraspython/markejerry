from pyrogram import Client, filters
import os
import time
import asyncio

PROGRESS_BAR = """<b>
╭━━━━❰ ᴘʀᴏɢʀᴇss ʙᴀʀ ❱━➣
┣⪼ 🗃️ Sɪᴢᴇ: {1} | {2}
┣⪼ ⏳️ Dᴏɴᴇ: {0}%
┣⪼ 🚀 Sᴩᴇᴇᴅ: {3}/s
┣⪼ ⏰️ Eᴛᴀ: {4}
╰━━━━━━━━━━━━━━━➣ 
</b>"""

@Client.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text("Hello! 👋 I'm a File Renamer Bot.\n\nSend me a document, video, or audio file, and I'll rename it for you!")

@Client.on_message(filters.command("help"))
async def help_command(client, message):
    await message.reply_text("🔹 **How to Use:**\n1️⃣ Send me a document, video, or audio file.\n2️⃣ I'll ask for the new name.\n3️⃣ Reply with the new name (without extension).\n4️⃣ I will rename & send it back to you.")

@Client.on_message(filters.document | filters.video | filters.audio)
async def ask_new_filename(client, message):
    file_name = message.document.file_name if message.document else message.video.file_name if message.video else message.audio.file_name
    ask_msg = await message.reply_text(f"📝 **Old File Name:** `{file_name}`\n\nSend me the new file name (without extension):")

    try:
        response = await client.listen(message.chat.id, timeout=60)
        new_name = response.text.strip()
        file_ext = os.path.splitext(file_name)[1]
        new_filename = new_name + file_ext
    except asyncio.TimeoutError:
        await message.reply_text("❌ You took too long to respond!")
        return

    file_path = await message.download()
    new_path = os.path.join(os.path.dirname(file_path), new_filename)
    os.rename(file_path, new_path)

    start_time = time.time()
    await message.reply_text(f"⏳ **Renaming in progress...**")
    
    # Progress simulation
    for progress in range(0, 101, 10):
        elapsed_time = time.time() - start_time
        speed = round((progress / 100) * os.path.getsize(new_path) / elapsed_time, 2) if elapsed_time > 0 else 0
        eta = round((100 - progress) * (elapsed_time / (progress + 1)), 2) if progress > 0 else "Calculating..."
        progress_text = PROGRESS_BAR.format(progress, os.path.getsize(new_path), os.path.getsize(file_path), speed, eta)
        await ask_msg.edit(progress_text)
        await asyncio.sleep(1)

    await message.reply_document(new_path, caption=f"✅ **Renamed to:** `{new_filename}`")
    os.remove(new_path)
