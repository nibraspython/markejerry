from motor.motor_asyncio import AsyncIOMotorClient
from config import Config
from .utils import send_log

class Database:
    def __init__(self, uri, database_name):
        self._client = AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.user

    def new_user(self, id):
        return dict(
            _id=int(id),                                   
            file_id=None,
            caption=None,
            saved_file=None  # ✅ Added field for saved file
        )

    async def add_user(self, b, m):
        u = m.from_user
        if not await self.is_user_exist(u.id):
            user = self.new_user(u.id)
            await self.col.insert_one(user)            
            await send_log(b, u)

    async def is_user_exist(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return bool(user)

    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_users(self):
        all_users = self.col.find({})
        return all_users

    async def delete_user(self, user_id):
        await self.col.delete_many({'_id': int(user_id)})

    async def set_thumbnail(self, id, file_id):
        await self.col.update_one({'_id': int(id)}, {'$set': {'file_id': file_id}})

    async def get_thumbnail(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('file_id', None)

    async def set_caption(self, id, caption):
        await self.col.update_one({'_id': int(id)}, {'$set': {'caption': caption}})

    async def get_caption(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('caption', None)

    # ✅ Added functions to save & retrieve renamed files
    async def save_file(self, user_id, file_name, file_id):
        """Save renamed file details to the database"""
        await self.col.update_one(
            {"_id": int(user_id)},
            {"$set": {"saved_file": {"file_name": file_name, "file_id": file_id}}},
            upsert=True
        )

    async def get_file(self, user_id):
        """Retrieve file details for the user"""
        user = await self.col.find_one({"_id": int(user_id)})
        return user.get("saved_file", None) if user else None

db = Database(Config.DB_URL, Config.DB_NAME)
