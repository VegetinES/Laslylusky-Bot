import random
import discord
import datetime
import re
from .level_db import LevelDatabase
from .constants import (
    XP_BASE, XP_PER_WORD, XP_MAX_WORDS, XP_MIN, XP_MAX, 
    XP_COOLDOWN, calculate_xp_for_next_level, get_level_from_xp
)

class LevelManager:
    def __init__(self, bot):
        self.bot = bot
        self.db = LevelDatabase()
    
    def get_guild_config(self, guild_id):
        return self.db.get_guild_config(guild_id)
    
    def update_guild_config(self, guild_id, update_data):
        self.db.update_guild_config(guild_id, update_data)
    
    def get_user_level(self, guild_id, user_id):
        user_data = self.db.get_user_level(guild_id, user_id)
        level, remaining_xp = get_level_from_xp(user_data["xp"])
        user_data["level"] = level
        return user_data
    
    def calculate_message_xp(self, message):
        content = message.content.strip()
        content = re.sub(r'\s+', ' ', content)
        words = content.split()
        word_count = min(len(words), XP_MAX_WORDS)
        
        xp = XP_BASE + (word_count * XP_PER_WORD)
        
        xp = max(XP_MIN, min(xp, XP_MAX))
        
        return round(xp)
    
    async def process_message(self, message):
        if not message.guild or message.author.bot:
            return None
        
        config = self.get_guild_config(message.guild.id)
        if not config["enabled"]:
            return None
        
        if not self.db.check_cooldown(message.guild.id, message.author.id, XP_COOLDOWN):
            return None
        
        if message.channel.id in config["excluded_channels"]:
            return None
        
        for role_id in config["excluded_roles"]:
            role = message.guild.get_role(role_id)
            if role and role in message.author.roles:
                return None
        
        xp_to_add = self.calculate_message_xp(message)
        
        multiplier = config["multiplier"]
        if multiplier != 1.0 and config.get("multiplier_end_time"):
            end_time = datetime.datetime.fromisoformat(config["multiplier_end_time"])
            if datetime.datetime.utcnow() > end_time:
                self.update_guild_config(message.guild.id, {
                    "multiplier": 1.0,
                    "multiplier_end_time": None
                })
                multiplier = 1.0
        
        if multiplier != 1.0:
            xp_to_add = int(xp_to_add * multiplier)
        
        old_data = self.get_user_level(message.guild.id, message.author.id)
        old_level = old_data["level"]
        
        updated_data = self.db.add_xp_to_user(message.guild.id, message.author.id, xp_to_add)
        new_data = self.get_user_level(message.guild.id, message.author.id)
        new_level = new_data["level"]
        
        if new_level > old_level:
            await self.handle_level_up(message, new_level, old_level)
            await self.handle_role_rewards(message.guild, message.author, new_level)
        
        return new_data
    
    async def handle_level_up(self, message, new_level, old_level):
        config = self.get_guild_config(message.guild.id)
        
        if not config["announcement"]["enabled"]:
            return
        
        announcement_msg = config["announcement"]["message"]
        announcement_msg = announcement_msg.replace("{usuario}", message.author.mention)
        announcement_msg = announcement_msg.replace("{nivel}", str(new_level))
        
        channel_type = config["announcement"]["channel_type"]
        
        if channel_type == "dm":
            try:
                await message.author.send(announcement_msg)
            except:
                pass
        elif channel_type == "same":
            await message.channel.send(announcement_msg)
        elif channel_type == "custom" and config["announcement"]["custom_channel_id"]:
            channel_id = config["announcement"]["custom_channel_id"]
            channel = message.guild.get_channel(channel_id)
            if channel:
                await channel.send(announcement_msg)
    
    async def handle_role_rewards(self, guild, member, new_level):
        config = self.get_guild_config(guild.id)
        reward_roles = config.get("reward_roles", {})
        
        roles_to_add = []
        
        for level_str, role_id in reward_roles.items():
            level = int(level_str)
            if level <= new_level:
                role = guild.get_role(role_id)
                if role and role not in member.roles:
                    roles_to_add.append(role)
        
        if roles_to_add:
            try:
                await member.add_roles(*roles_to_add, reason="Level rewards")
            except:
                pass
    
    def set_user_level(self, guild_id, user_id, level):
        return self.db.set_user_level(guild_id, user_id, level)
    
    def transfer_level(self, guild_id, from_user_id, to_user_id):
        return self.db.transfer_level(guild_id, from_user_id, to_user_id)
    
    def get_top_users(self, guild_id, page=0, limit=10):
        skip = page * limit
        return self.db.get_top_users(guild_id, skip, limit)
    
    def get_user_rank(self, guild_id, user_id):
        return self.db.get_user_rank(guild_id, user_id)
    
    def count_ranked_users(self, guild_id):
        return self.db.count_ranked_users(guild_id)
    
    def reset_user_level(self, guild_id, user_id):
        self.db.reset_user_level(guild_id, user_id)