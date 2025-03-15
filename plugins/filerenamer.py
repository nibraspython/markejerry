from pyrogram import Client, filters
import os
import time
import math

PROGRESS_BAR = """<b>\n
╭━━━━❰ ᴘʀᴏɢʀᴇss ʙᴀʀ ❱━➣
┣⪼ 🗃️ Sɪᴢᴇ: {1} | {2}
┣⪼ ⏳️ Dᴏɴᴇ : {0}%
┣⪼ 🚀 Sᴩᴇᴇᴅ: {3}/s
┣⪼ ⏰️ Eᴛᴀ: {4}
╰━━━━━━━━━━━━━━━➣ </b>"""

async def progress_callback(current, total, message, start_time):
    """Progress bar for file operations"""
    now = time.time()
    diff = now - start_time
    if diff == 0:
        return
    
    # Calculate percentage
    percentage = current * 100 / total
    
    # Calculate speed
    speed = current / diff
    
    # Calculate ETA (Estimated Time Remaining)
    if speed > 0:
        eta = (total - current) / speed
    else:
        eta = 0

    # Convert sizes to readable format
    current_size = human_readable_size(current)
    total_size = human_readable_size(total)
    speed_readable = human_readable_size(speed)

    # Generate progress bar
    progress = PROGRESS_BAR.format(
        math.floor(percentage),
        current_size,
        total_size,
        speed_readable,
        time.strftime("%H:%M:%S", time.gmtime(eta))
    )

    try:
        await message.edit(progress)
    except:
        pass  # Ignore message edit errors if they happen

def human_readable_size(size):
    """Convert bytes to human-readable format"""
    units = ["B", "KB", "MB", "GB", "TB"]
    index = 0
    while size >= 1024 and index < len(units) - 1:
        size /= 1024
        index += 1
    return f"{size:.2f} {units[index]}"

@Client.on_message(filters.document | filters.video | filters.audio)
async def ask_new_filename(client, message):
    file_name = message.document.file_name if message.document else message.video.file_name if message.video else message.audio.file_name
    reply = await message.reply_text(f"Old File Name: `{file_name}`\n\nSend me the new file name (without extension)")

    response = await client.listen(message.chat.id, timeout=60)
    new_name = response.text.strip()
    file_ext = os.path.splitext(file_name)[1]
    new_filename = new_name + file_ext

    # Download file with progress bar
    start_time = time.time()
    file_path = await client.download_media(
        message, 
        progress=progress_callback, 
        progress_args=(reply, start_time)
    )

    # Rename file
    new_path = file_path.replace(file_name, new_filename)
    os.rename(file_path, new_path)

    # Upload file with progress bar
    start_time = time.time()
    await client.send_document(
        message.chat.id,
        new_path,
        caption=f"✅ Renamed to `{new_filename}`",
        progress=progress_callback,
        progress_args=(reply, start_time)
    )

    # Remove the file after sending
    os.remove(new_path)

    # Delete the progress message after completion
    await reply.delete()
