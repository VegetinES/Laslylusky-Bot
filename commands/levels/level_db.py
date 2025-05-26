import pymongo
import datetime
from .constants import DEFAULT_CONFIG

class LevelDatabase:
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client["discord_bot"]
        self.guild_configs = self.db["level_configs"]
        self.user_levels = self.db["user_levels"]
        self.xp_cooldowns = {}
    
    def get_guild_config(self, guild_id):
        config = self.guild_configs.find_one({"guild_id": guild_id})
        if not config:
            config = DEFAULT_CONFIG.copy()
            config["guild_id"] = guild_id
            self.guild_configs.insert_one(config)
        return config

    def update_guild_config(self, guild_id, update_data):
        flat_update = {}
        
        for key, value in update_data.items():
            if "." in key:
                flat_update[key] = value
            else:
                flat_update[key] = value
                
        self.guild_configs.update_one(
            {"guild_id": guild_id},
            {"$set": flat_update},
            upsert=True
        )
    
    def get_user_level(self, guild_id, user_id):
        user_data = self.user_levels.find_one({"guild_id": guild_id, "user_id": user_id})
        if not user_data:
            user_data = {
                "guild_id": guild_id,
                "user_id": user_id,
                "xp": 0,
                "level": 0,
                "messages": 0,
                "last_message": None
            }
            self.user_levels.insert_one(user_data)
        return user_data
    
    def update_user_level(self, guild_id, user_id, update_data):
        self.user_levels.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {"$set": update_data},
            upsert=True
        )
    
    def add_xp_to_user(self, guild_id, user_id, xp_to_add):
        user_data = self.get_user_level(guild_id, user_id)
        
        user_data["xp"] += xp_to_add
        user_data["messages"] += 1
        user_data["last_message"] = datetime.datetime.utcnow()
        
        self.update_user_level(guild_id, user_id, user_data)
        return user_data
    
    def set_user_level(self, guild_id, user_id, level):
        from .constants import get_total_xp_for_level
        xp = get_total_xp_for_level(level)
        
        user_data = self.get_user_level(guild_id, user_id)
        user_data["xp"] = xp
        user_data["level"] = level
        
        self.update_user_level(guild_id, user_id, user_data)
        return user_data
    
    def transfer_level(self, guild_id, from_user_id, to_user_id):
        from_user = self.get_user_level(guild_id, from_user_id)
        to_user = self.get_user_level(guild_id, to_user_id)
        
        to_user["xp"] += from_user["xp"]
        to_user["messages"] += from_user["messages"]
        
        from_user["xp"] = 0
        from_user["messages"] = 0
        from_user["level"] = 0
        
        self.update_user_level(guild_id, from_user_id, from_user)
        self.update_user_level(guild_id, to_user_id, to_user)
        
        return from_user, to_user
    
    def get_top_users(self, guild_id, skip=0, limit=10):
        users = list(self.user_levels.find(
            {"guild_id": guild_id},
            sort=[("xp", pymongo.DESCENDING)],
            skip=skip,
            limit=limit
        ))
        return users
    
    def get_user_rank(self, guild_id, user_id):
        user_data = self.get_user_level(guild_id, user_id)
        rank = self.user_levels.count_documents({
            "guild_id": guild_id,
            "xp": {"$gt": user_data["xp"]}
        }) + 1
        return rank
    
    def count_ranked_users(self, guild_id):
        return self.user_levels.count_documents({"guild_id": guild_id, "xp": {"$gt": 0}})
    
    def check_cooldown(self, guild_id, user_id, cooldown_seconds=60):
        key = f"{guild_id}:{user_id}"
        now = datetime.datetime.utcnow().timestamp()
        
        if key in self.xp_cooldowns:
            if now - self.xp_cooldowns[key] < cooldown_seconds:
                return False
        
        self.xp_cooldowns[key] = now
        return True
    
    def reset_user_level(self, guild_id, user_id):
        self.user_levels.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {"$set": {"xp": 0, "level": 0}}
        )