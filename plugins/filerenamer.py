from pyrogram import Client, filters
import os
import time
import asyncio

# Progress Bar Function
async def progress_bar(current, total, message):
    percent = (current / total) * 100
    progress = "▓" * int(percent // 5) + "░" * (20 - int(percent // 5))
    speed = current / (time.time() - message.start_time + 1)
    eta = (total - current) / speed if speed > 0 else 0

    progress_text = f"""
<b>
╭━━━━❰ ᴘʀᴏɢʀᴇss ʙᴀʀ ❱━➣
┣⪼ 📂 Sɪᴢᴇ: {total / 1024:.2f} KB
┣⪼ ⏳ Dᴏɴᴇ: {percent:.2f}%
┣⪼ 🚀 Sᴩᴇᴇᴅ: {speed / 1024:.2f} KB/s
┣⪼ ⏰ Eᴛᴀ: {eta:.2f} s
┣⪼ [{progress}]
╰━━━━━━━━━━━━━━━➣
</b>"""

    await message.edit(progress_text)


# File Rename Handler
@Client.on_message(filters.document | filters.video | filters.audio)
async def ask_new_filename(client, message):
    file_name = message.document.file_name if message.document else message.video.file_name if message.video else message.audio.file_name
    sent_msg = await message.reply_text(f"📁 Old File Name: `{file_name}`\n\n✏️ Send me the new file name (without extension).")

    try:
        # Wait for the user to send a new filename
        response = await client.listen(filters.text & filters.private, timeout=60)
        new_name = response.text.strip()
        file_ext = os.path.splitext(file_name)[1]
        new_filename = new_name + file_ext

        # Start downloading the file
        file_path = await message.download(progress=progress_bar, progress_args=(sent_msg,))
        new_path = file_path.replace(file_name, new_filename)
        os.rename(file_path, new_path)

        # Send the renamed file
        await message.reply_document(new_path, caption=f"✅ Renamed to `{new_filename}`")
        os.remove(new_path)

    except asyncio.TimeoutError:
        await message.reply_text("❌ You took too long to respond. Try again!")

