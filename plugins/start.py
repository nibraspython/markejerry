

@Client.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text("Hello! 👋 I'm a File Renamer Bot.\n\nSend me a document, video, or audio file, and I'll rename it for you!")

@Client.on_message(filters.command("help"))
async def help_command(client, message):
    await message.reply_text("🔹 **How to Use:**\n1️⃣ Send me a document, video, or audio file.\n2️⃣ I'll ask for the new name.\n3️⃣ Reply with the new name (without extension).\n4️⃣ I will rename & send it back to you.")
