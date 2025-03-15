from pyrogram import Client, filters
from pyrogram.enums import MessageMediaType
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from helper.utils import progress_for_pyrogram, convert, humanbytes
from asyncio import sleep
from PIL import Image
import os, time

@Client.on_message(filters.private & (filters.document | filters.audio | filters.video))
async def rename_handler(client, message):
    file = getattr(message, message.media.value, None)
    if not file:
        return await message.reply_text("❌ Unable to process this file type.")
    
    filename = file.file_name
    if file.file_size > 2000 * 1024 * 1024:
        return await message.reply_text("❌ This bot does not support files larger than 2GB.")
    
    try:
        await message.reply_text(
            text=f"**📂 Old Filename:** `{filename}`\n\n✏️ Send me the new file name (without extension).",
            reply_to_message_id=message.id,
            reply_markup=ForceReply(True)
        )
    except FloodWait as e:
        await sleep(e.value)
        await message.reply_text(
            text=f"**📂 Old Filename:** `{filename}`\n\n✏️ Send me the new file name (without extension).",
            reply_to_message_id=message.id,
            reply_markup=ForceReply(True)
        )
    except:
        pass

@Client.on_message(filters.private & filters.reply & filters.text)
async def rename_selection(client, message):
    reply_message = message.reply_to_message
    if not reply_message or not reply_message.reply_markup:
        return
    
    new_name = message.text.strip()
    await message.delete()
    file = reply_message.reply_to_message
    media = getattr(file, file.media.value, None)
    if not media:
        return await message.reply_text("❌ Unable to fetch file details.")
    
    if '.' not in new_name:
        extn = media.file_name.rsplit('.', 1)[-1] if '.' in media.file_name else "mkv"
        new_name += f".{extn}"
    
    await reply_message.delete()
    button = [[InlineKeyboardButton("📁 Document", callback_data=f"upload_document|{new_name}")]]
    if file.media in [MessageMediaType.VIDEO, MessageMediaType.DOCUMENT]:
        button.append([InlineKeyboardButton("🎥 Video", callback_data=f"upload_video|{new_name}")])
    elif file.media == MessageMediaType.AUDIO:
        button.append([InlineKeyboardButton("🎵 Audio", callback_data=f"upload_audio|{new_name}")])
    
    await message.reply_text(
        text=f"**✅ File renamed to:** `{new_name}`\n\nChoose output format:",
        reply_to_message_id=file.id,
        reply_markup=InlineKeyboardMarkup(button)
    )

@Client.on_callback_query(filters.regex("upload"))
async def rename_callback(bot, query):
    user_id = query.from_user.id
    callback_data = query.data.split("|")
    if len(callback_data) < 2:
        return await query.message.edit("❌ Invalid request.")
    
    file_type, file_name = callback_data
    file = query.message.reply_to_message
    if not file:
        return await query.message.edit("❌ Original file not found.")
    
    file_path = f"downloads/{user_id}_{time.time()}/{file_name}"
    sts = await query.message.edit("📥 Downloading file...")
    
    try:
        path = await file.download(file_name=file_path, progress=progress_for_pyrogram, progress_args=("Downloading...", sts, time.time()))
    except Exception as e:
        return await sts.edit(f"❌ Error: {e}")
    
    await sts.edit("📤 Uploading file...")
    try:
        if file_type == "upload_document":
            await sts.reply_document(document=file_path, caption=f"**{file_name}**")
        elif file_type == "upload_video":
            await sts.reply_video(video=file_path, caption=f"**{file_name}**")
        elif file_type == "upload_audio":
            await sts.reply_audio(audio=file_path, caption=f"**{file_name}**")
    except Exception as e:
        return await sts.edit(f"❌ Upload error: {e}")
    
    try:
        os.remove(file_path)
        await sts.delete()
    except:
        pass
