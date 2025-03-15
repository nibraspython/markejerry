from pyrogram import Client, filters
from pyrogram.enums import MessageMediaType
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from helper.utils import progress_for_pyrogram, convert, humanbytes
from helper.database import db
from asyncio import sleep
from PIL import Image
import os, time

# ✅ Step 1: Ask for a new file name
@Client.on_message(filters.private & (filters.document | filters.audio | filters.video))
async def rename_handler(client, message):
    file = getattr(message, message.media.value)
    filename = file.file_name  

    # ✅ File size limit check (2GB)
    if file.file_size > 2000 * 1024 * 1024:
        return await message.reply_text("❌ This bot does not support files larger than 2GB.")

    # ✅ Send a Force Reply message to get new filename
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

# ✅ Step 2: Capture the user’s response & show rename options
async def force_reply_filter(_, client, message):
    if (message.reply_to_message.reply_markup) and isinstance(message.reply_to_message.reply_markup, ForceReply):
        return True 
    return False 

@Client.on_message(filters.private & filters.reply & filters.create(force_reply_filter))
async def rename_selection(client, message):
    reply_message = message.reply_to_message

    new_name = message.text.strip()
    await message.delete()  # ✅ Delete user input
    msg = await client.get_messages(message.chat.id, reply_message.id)
    file = msg.reply_to_message
    media = getattr(file, file.media.value)

    # ✅ Auto-detect file extension if not provided
    if "." not in new_name:
        extn = media.file_name.rsplit('.', 1)[-1] if "." in media.file_name else "mkv"
        new_name = new_name + "." + extn

    await reply_message.delete()

    # ✅ Show output file type selection
    button = [[InlineKeyboardButton("📁 Document", callback_data=f"upload_document_{new_name}")]]
    if file.media in [MessageMediaType.VIDEO, MessageMediaType.DOCUMENT]:
        button.append([InlineKeyboardButton("🎥 Video", callback_data=f"upload_video_{new_name}")])
    elif file.media == MessageMediaType.AUDIO:
        button.append([InlineKeyboardButton("🎵 Audio", callback_data=f"upload_audio_{new_name}")])
    
    await message.reply(
        text=f"**✅ File renamed to:** `{new_name}`\n\nChoose output format:",
        reply_to_message_id=file.id,
        reply_markup=InlineKeyboardMarkup(button)
    )

# ✅ Step 3: Download, rename, and upload file
@Client.on_callback_query(filters.regex("upload_"))
async def rename_callback(bot, query): 
    user_id = query.from_user.id
    callback_data = query.data.split("_", 2)  # Fixing index out of range issue
    file_type = callback_data[1]
    file_name = callback_data[2]

    file = query.message.reply_to_message
    file_path = f"downloads/{user_id}_{int(time.time())}/{file_name}"

    sts = await query.message.edit("📥 Downloading file...")    
    try:
        path = await file.download(file_name=file_path, progress=progress_for_pyrogram, progress_args=("Downloading...", sts, time.time()))                    
    except Exception as e:
        return await sts.edit(f"❌ Error: {e}")
    
    # ✅ Get file metadata
    duration = 0
    try:
        metadata = extractMetadata(createParser(file_path))
        if metadata.has("duration"): duration = metadata.get('duration').seconds
    except:
        pass

    ph_path = None
    media = getattr(file, file.media.value)
    db_caption = await db.get_caption(user_id)
    db_thumb = await db.get_thumbnail(user_id)

    # ✅ Set custom caption
    if db_caption:
        try:
            caption = db_caption.format(filename=file_name, filesize=humanbytes(media.file_size), duration=convert(duration))
        except KeyError:
            caption = f"**{file_name}**"
    else:
        caption = f"**{file_name}**"

    # ✅ Generate thumbnail
    if media.thumbs or db_thumb:
        ph_path = await bot.download_media(db_thumb if db_thumb else media.thumbs[0].file_id)
        Image.open(ph_path).convert("RGB").save(ph_path)
        img = Image.open(ph_path)
        img.resize((320, 320))
        img.save(ph_path, "JPEG")

    await sts.edit("📤 Uploading file...")

    try:
        if file_type == "document":
            await sts.reply_document(
                document=file_path,
                thumb=ph_path, 
                caption=caption, 
                progress=progress_for_pyrogram,
                progress_args=("Uploading...", sts, time.time())
            )
        elif file_type == "video": 
            await sts.reply_video(
                video=file_path,
                caption=caption,
                thumb=ph_path,
                duration=duration,
                progress=progress_for_pyrogram,
                progress_args=("Uploading...", sts, time.time())
            )
        elif file_type == "audio": 
            await sts.reply_audio(
                audio=file_path,
                caption=caption,
                thumb=ph_path,
                duration=duration,
                progress=progress_for_pyrogram,
                progress_args=("Uploading...", sts, time.time())
            )
    except Exception as e:          
        try: 
            os.remove(file_path)
            if ph_path: os.remove(ph_path)
            return await sts.edit(f"❌ Upload error: {e}")
        except:
            pass
        
    try: 
        os.remove(file_path)
        if ph_path: os.remove(ph_path)
        await sts.delete()
    except:
        pass  
