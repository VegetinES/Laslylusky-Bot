import discord
from discord.ext import tasks, commands
import asyncio
from datetime import datetime, timedelta
import pytz
from .database import BirthdayDB
from .utils import format_mentions, parse_timezone

class BirthdayTask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = BirthdayDB()
        self.check_hour_cache = {}
        self.birthday_task.start()
        print("🎂 Sistema de cumpleaños iniciado y esperando")

    def cog_unload(self):
        self.birthday_task.cancel()

    @tasks.loop(seconds=30.0)
    async def birthday_task(self):
        try:
            if not self.bot.is_ready():
                return

            now_utc = datetime.now(pytz.UTC)
            
            for guild in self.bot.guilds:
                try:
                    config = await self.db.get_config(guild.id)
                    if not config:
                        continue
                    
                    timezone_str = config.get("timezone", "UTC+00:00")
                    tz_offset_str = timezone_str.replace("UTC", "")
                    minutes_offset = parse_timezone(tz_offset_str)
                    
                    if minutes_offset is None:
                        continue
                    
                    timezone_offset = timedelta(minutes=minutes_offset)
                    guild_time = now_utc + timezone_offset
                    
                    key = f"{guild.id}_{guild_time.day}_{guild_time.month}"
                    
                    if guild_time.hour == 0 and (0 <= guild_time.minute < 5):
                        if key in self.check_hour_cache:
                            continue
                        
                        self.check_hour_cache[key] = True
                        
                        for old_key in list(self.check_hour_cache.keys()):
                            parts = old_key.split('_')
                            old_guild_id, old_day, old_month = parts
                            if f"{old_day}_{old_month}" != f"{guild_time.day}_{guild_time.month}":
                                del self.check_hour_cache[old_key]
                        
                        print(f"🎂 Verificando cumpleaños para {guild.name} - {guild_time.day}/{guild_time.month} - {guild_time.hour}:{guild_time.minute}")
                        await self.check_birthdays(guild.id, guild_time.day, guild_time.month)
                
                except Exception as e:
                    print(f"Error procesando cumpleaños para guild {guild.id}: {e}")
                    
        except Exception as e:
            print(f"Error general en birthday_task: {e}")

    @birthday_task.before_loop
    async def before_birthday_task(self):
        await self.bot.wait_until_ready()
        print("🎂 Tarea de cumpleaños iniciada y esperando")

    async def check_birthdays(self, guild_id, day, month):
        try:
            guild = self.bot.get_guild(guild_id)
            if not guild:
                return
            
            config = await self.db.get_config(guild_id)
            if not config:
                return
            
            channel_id = config.get("channel_id")
            if not channel_id:
                return
            
            channel = guild.get_channel(channel_id)
            if not channel:
                return
            
            birthdays = await self.db.get_todays_birthdays(day, month)
            guild_birthdays = [b for b in birthdays if b["guild_id"] == guild_id]
            
            if not guild_birthdays:
                print(f"🎂 No hay cumpleaños hoy para {guild.name}")
                return
            
            birthday_users = []
            for birthday in guild_birthdays:
                user_id = birthday["user_id"]
                member = guild.get_member(user_id)
                if member:
                    birthday_users.append(member)
            
            if not birthday_users:
                print(f"🎂 No hay miembros activos con cumpleaños hoy en {guild.name}")
                return
            
            message_template = config.get("message", "¡Feliz cumpleaños [@users]! 🎂🎉")
            formatted_message = format_mentions(birthday_users, message_template)
            
            print(f"🎂 Enviando mensaje de cumpleaños en {guild.name} para: {', '.join([u.name for u in birthday_users])}")
            await channel.send(formatted_message)
            print(f"🎂 Mensaje enviado correctamente en {guild.name}")
            
        except Exception as e:
            print(f"Error verificando cumpleaños: {e}")