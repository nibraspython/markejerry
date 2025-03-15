from pyrogram import Client, filters
import os
import asyncio
import time
from pyroask import Ask  # ✅ Import PyroAsk

PROGRESS_BAR = """<b>\n
╭━━━━❰ ᴘʀᴏɢʀᴇss ʙᴀʀ ❱━➣
┣⪼ 🗃️ Sɪᴢᴇ: {1} | {2}
┣⪼ ⏳️ Dᴏɴᴇ : {0}%
┣⪼ 🚀 Sᴩᴇᴇᴅ: {3}/s
┣⪼ ⏰️ Eᴛᴀ: {4}
╰━━━━━━━━━━━━━━━➣ </b>"""

# ✅ Start Command
@Client.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text(
        "👋 **Hello!**\n\nI am a **File Renamer Bot**. Send me a file, and I will rename it for you!\n\nUse /help for more details."
    )

# ✅ Help Command
@Client.on_message(filters.command("help"))
async def help_command(client, message):
    await message.reply_text(
        "**📌 How to Use the Bot:**\n\n"
        "1️⃣ Send me any document, video, or audio file.\n"
        "2️⃣ I will ask for a new name (without extension).\n"
        "3️⃣ Reply with the new name.\n"
        "4️⃣ I will rename and send you the updated file! ✅"
    )

@Client.on_message(filters.document | filters.video | filters.audio)
async def ask_new_filename(client, message):
    file_name = (
        message.document.file_name
        if message.document else message.video.file_name
        if message.video else message.audio.file_name
    )

    # ✅ Automatically replying to the same message
    reply_msg = await message.reply_text(
        f"📂 **Old File Name:** `{file_name}`\n\n✍️ Send me the new file name (without extension)",
        reply_to_message_id=message.id
    )

    try:
        # ✅ Using PyroAsk for user input
        ask = Ask(client)
        response = await ask.question(message.chat.id, "Send new file name:", timeout=60)
        new_name = response.text.strip()
    except asyncio.TimeoutError:
        await reply_msg.edit_text("⏳ You took too long! Please send the file again.")
        return
    
    file_ext = os.path.splitext(file_name)[1]
    new_filename = new_name + file_ext

    # ✅ Download the file
    file_path = await message.download()
    new_path = os.path.join(os.path.dirname(file_path), new_filename)

    os.rename(file_path, new_path)
    
    # ✅ Progress Bar Simulation
    file_size = os.path.getsize(new_path)
    start_time = time.time()
    
    for progress in range(0, 101, 10):
        elapsed_time = time.time() - start_time
        speed = (progress / 100) * file_size / (elapsed_time + 1)
        eta = (100 - progress) * elapsed_time / (progress + 1)
        await reply_msg.edit_text(
            PROGRESS_BAR.format(progress, file_size, file_size, round(speed, 2), round(eta, 2)),
            parse_mode="html"
        )
        await asyncio.sleep(1)

    await message.reply_document(new_path, caption=f"✅ Renamed to `{new_filename}`", reply_to_message_id=message.id)
    os.remove(new_path)
