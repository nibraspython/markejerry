import os

class Config:
    API_ID = int(os.getenv("API_ID"))
    API_HASH = os.getenv("API_HASH")
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    ADMIN = [int(i) for i in os.getenv("ADMIN", "").split() if i.isdigit()]
    LOG_CHANNEL = int(os.getenv("LOG_CHANNEL")) if os.getenv("LOG_CHANNEL") else None
    WEB_SUPPORT = bool(os.getenv("WEB_SUPPORT", true))
    MAX_CONCURRENT_TRANSMISSIONS = 5
    BOT_UPTIME = "Bot is running..."
