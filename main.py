from datetime import datetime
from pytz import timezone
from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from aiohttp import web
import os
from config import Config

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="renamer",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            workers=min(32, os.cpu_count() + 4),
            plugins={"root": "plugins"},  # ✅ Ensure the "plugins" folder is used
            sleep_threshold=15,
            max_concurrent_transmissions=Config.MAX_CONCURRENT_TRANSMISSIONS,
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.mention = me.mention
        self.username = me.username  
        self.uptime = Config.BOT_UPTIME     
        
        if Config.WEB_SUPPORT:
            app = web.Application(client_max_size=30000000)
            app.add_routes([web.get("/", self.web_status)])  # ✅ Added a simple route
            runner = web.AppRunner(app)
            await runner.setup()
            port = int(os.getenv("PORT", 8080))  # ✅ Added PORT environment variable
            await web.TCPSite(runner, "0.0.0.0", port).start()

        print(f"\033[1;96m @{me.username} Sᴛᴀʀᴛᴇᴅ......⚡️⚡️⚡️\033[0m")
        try: [await self.send_message(id, f"**__{me.first_name}  Iꜱ Sᴛᴀʀᴛᴇᴅ.....✨️__**") for id in Config.ADMIN]                               
        except: pass

    async def web_status(self, request):
        return web.Response(text="Bot is Running")

Bot().run()
