import pymongo
import asyncio
from typing import Dict, List, Optional, Any

class BirthdayDB:
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client["birthday_bot"]
        self.birthdays = self.db["birthdays"]
        self.config = self.db["config"]
        
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        self.birthdays.create_index([("user_id", 1), ("guild_id", 1)], unique=True)
        self.birthdays.create_index([("guild_id", 1), ("month", 1), ("day", 1)])
        self.config.create_index([("guild_id", 1)], unique=True)
    
    async def get_config(self, guild_id: int) -> Optional[Dict[str, Any]]:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, 
            lambda: self.config.find_one({"guild_id": guild_id})
        )
        if result:
            result.pop("_id", None)
        return result
    
    async def save_config(self, config_data: Dict[str, Any]) -> bool:
        guild_id = config_data["guild_id"]
        loop = asyncio.get_event_loop()
        
        try:
            await loop.run_in_executor(
                None,
                lambda: self.config.update_one(
                    {"guild_id": guild_id},
                    {"$set": config_data},
                    upsert=True
                )
            )
            return True
        except Exception as e:
            print(f"Error al guardar configuración: {e}")
            return False
    
    async def delete_config(self, guild_id: int) -> bool:
        loop = asyncio.get_event_loop()
        
        try:
            await loop.run_in_executor(
                None,
                lambda: self.config.delete_one({"guild_id": guild_id})
            )
            return True
        except Exception as e:
            print(f"Error al eliminar configuración: {e}")
            return False
    
    async def set_birthday(self, user_data: Dict[str, Any]) -> bool:
        user_id = user_data["user_id"]
        guild_id = user_data["guild_id"]
        
        loop = asyncio.get_event_loop()
        
        try:
            await loop.run_in_executor(
                None,
                lambda: self.birthdays.update_one(
                    {"user_id": user_id, "guild_id": guild_id},
                    {"$set": user_data},
                    upsert=True
                )
            )
            return True
        except Exception as e:
            print(f"Error al establecer cumpleaños: {e}")
            return False
    
    async def get_birthday(self, user_id: int, guild_id: int) -> Optional[Dict[str, Any]]:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, 
            lambda: self.birthdays.find_one({"user_id": user_id, "guild_id": guild_id})
        )
        if result:
            result.pop("_id", None)
        return result
    
    async def delete_birthday(self, user_id: int, guild_id: int) -> bool:
        loop = asyncio.get_event_loop()
        
        try:
            await loop.run_in_executor(
                None,
                lambda: self.birthdays.delete_one({"user_id": user_id, "guild_id": guild_id})
            )
            return True
        except Exception as e:
            print(f"Error al eliminar cumpleaños: {e}")
            return False
    
    async def get_todays_birthdays(self, day: int, month: int) -> List[Dict[str, Any]]:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, 
            lambda: list(self.birthdays.find({"day": day, "month": month}))
        )
        for item in result:
            item.pop("_id", None)
        return result

    async def delete_all_guild_birthdays(self, guild_id: int) -> bool:
        loop = asyncio.get_event_loop()
        
        try:
            await loop.run_in_executor(
                None,
                lambda: self.birthdays.delete_many({"guild_id": guild_id})
            )
            return True
        except Exception as e:
            print(f"Error al eliminar todos los cumpleaños del servidor: {e}")
            return False