import discord
import asyncio
import datetime
import pytz
from typing import Dict, List, Any
from .database import BirthdayDB
from .utils import format_mentions, parse_timezone

class BirthdayScheduler:
    def __init__(self, bot):
        self.bot = bot
        self.db = BirthdayDB()
        self.running = False
        self.task = None
    
    def start(self):
        if not self.running:
            self.running = True
            self.task = asyncio.create_task(self.schedule_loop())
    
    def stop(self):
        if self.running:
            self.running = False
            if self.task:
                self.task.cancel()
            self.task = None
    
    async def schedule_loop(self):
        while self.running:
            now = datetime.datetime.now(pytz.UTC)
            
            guild_configs = await self.get_all_guild_configs()
            
            for guild_id, config in guild_configs.items():
                timezone_str = config.get("timezone", "UTC+00:00")
                minutes_offset = parse_timezone(timezone_str.replace("UTC", ""))
                if minutes_offset is None:
                    continue
                
                timezone_offset = datetime.timedelta(minutes=minutes_offset)
                guild_now = now + timezone_offset
                
                if guild_now.hour == 0 and guild_now.minute == 0:
                    await self.check_birthdays(guild_id, guild_now.day, guild_now.month, config)
            
            await asyncio.sleep(60)
    
    async def get_all_guild_configs(self) -> Dict[int, Dict[str, Any]]:
        guild_configs = {}
        
        for guild in self.bot.guilds:
            config = await self.db.get_config(guild.id)
            if config:
                guild_configs[guild.id] = config
        
        return guild_configs
    
    async def check_birthdays(self, guild_id: int, day: int, month: int, config: Dict[str, Any]):
        guild = self.bot.get_guild(guild_id)
        if not guild:
            return
        
        birthdays = await self.db.get_todays_birthdays(day, month)
        guild_birthdays = [b for b in birthdays if b["guild_id"] == guild_id]
        
        if not guild_birthdays:
            return
        
        channel_id = config.get("channel_id")
        if not channel_id:
            return
        
        channel = guild.get_channel(channel_id)
        if not channel:
            return
        
        birthday_users = []
        for birthday in guild_birthdays:
            user_id = birthday["user_id"]
            member = guild.get_member(user_id)
            if member:
                birthday_users.append(member)
        
        if not birthday_users:
            return
        
        message_template = config.get("message", "¡Feliz cumpleaños [@users]! 🎂🎉")
        formatted_message = format_mentions(birthday_users, message_template)
        
        try:
            await channel.send(formatted_message)
        except discord.HTTPException as e:
            print(f"Error sending birthday message to guild {guild_id}: {e}")
    
    async def force_check(self, guild_id: int):
        config = await self.db.get_config(guild_id)
        if not config:
            return False
        
        now = datetime.datetime.now()
        await self.check_birthdays(guild_id, now.day, now.month, config)
        return True