from pyrogram import Client, filters
import os
import asyncio

PROGRESS_BAR = """<b>\n
╭━━━━❰ᴘʀᴏɢʀᴇss ʙᴀʀ❱━➣
┣⪼ 🗃️ Sɪᴢᴇ: {1} | {2}
┣⪼ ⏳️ Dᴏɴᴇ : {0}%
┣⪼ 🚀 Sᴩᴇᴇᴅ: {3}/s
┣⪼ ⏰️ Eᴛᴀ: {4}
╰━━━━━━━━━━━━━━━➣ </b>"""

@Client.on_message(filters.document | filters.video | filters.audio)
async def ask_new_filename(client, message):
    file_name = message.document.file_name if message.document else message.video.file_name if message.video else message.audio.file_name
    await message.reply_text(f"Old File Name: `{file_name}`\n\nSend me the new file name (without extension)")
    
    response = await client.listen(message.chat.id, timeout=60)
    new_name = response.text.strip()
    file_ext = os.path.splitext(file_name)[1]
    new_filename = new_name + file_ext
    
    file_path = await message.download()
    new_path = file_path.replace(file_name, new_filename)
    os.rename(file_path, new_path)
    
    await message.reply_document(new_path, caption=f"✅ Renamed to `{new_filename}`")
    os.remove(new_path)
