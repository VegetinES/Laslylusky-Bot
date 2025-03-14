import discord
from discord.ext import commands
from database.get import get_specific_field
import asyncio

async def send_ban_log(bot, guild: discord.Guild, target: discord.User, moderator: discord.User = None, reason: str = None, source: str = "manual"):
    cog = bot.get_cog('BanLogs')
    if cog:
        await cog.handle_ban_event(guild, target, moderator, reason, source)

class BanLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.recent_bans = {}

    async def _clear_recent_ban(self, guild_id: int, user_id: int):
        await asyncio.sleep(5)
        if guild_id in self.recent_bans and user_id in self.recent_bans[guild_id]:
            del self.recent_bans[guild_id][user_id]

    async def handle_ban_event(self, guild: discord.Guild, target: discord.User, moderator: discord.User = None, reason: str = None, source: str = "manual"):
        if guild.id not in self.recent_bans:
            self.recent_bans[guild.id] = {}

        if source == "command":
            self.recent_bans[guild.id][target.id] = True
            await self.log_ban_event(guild, target, moderator, reason, source)
            self.bot.loop.create_task(self._clear_recent_ban(guild.id, target.id))
            return

        if target.id in self.recent_bans.get(guild.id, {}):
            return

        await self.log_ban_event(guild, target, moderator, reason, source)

    def replace_variables(self, text: str, target: discord.User, moderator: discord.User = None, reason: str = None) -> str:
        replacements = {
            "{usertag}": str(target),
            "{user}": target.mention if hasattr(target, "mention") else f"<@{target.id}>",
            "{userid}": str(target.id),
        }
        
        if moderator:
            replacements.update({
                "{mod}": moderator.mention if hasattr(moderator, "mention") else f"<@{moderator.id}>",
                "{modtag}": str(moderator),
                "{modid}": str(moderator.id),
            })
            
        if reason:
            replacements["{reason}"] = str(reason)
            
        result = text
        for key, value in replacements.items():
            result = result.replace(key, value)
        return result

    async def log_ban_event(self, guild: discord.Guild, target: discord.User, moderator: discord.User = None, reason: str = None, source: str = "manual"):
        try:
            guild_data = get_specific_field(guild.id, "audit_logs")
            if not guild_data or "ban" not in guild_data:
                return
            
            ban_config = guild_data["ban"]
            
            is_activated = ban_config.get("activated")
            if isinstance(is_activated, str):
                is_activated = is_activated.lower() == "true"
            
            if not is_activated:
                return
                
            log_channel_id = ban_config.get("log_channel")
            if not log_channel_id or log_channel_id == 0:
                return
            
            log_channel = self.bot.get_channel(int(log_channel_id))
            if not log_channel:
                return
            
            message_format = ban_config.get("ban_messages", "")
            if not message_format:
                return
                
            message_data = await self.parse_log_message(message_format, target, moderator, reason)
            
            if not message_data:
                return
            
            if "embed" in message_data:
                await log_channel.send(embed=message_data["embed"])
            else:
                await log_channel.send(message_data["content"])

        except Exception as e:
            print(f"Error en log_ban_event: {e}")

    async def parse_log_message(self, message: str, target: discord.User, moderator: discord.User = None, reason: str = None):
        try:
            if message.startswith("embed:"):
                parts = message[6:].split(" ")
                embed_data = {}
                
                current_key = None
                current_value = []
                
                for part in parts:
                    if part.startswith("tl:"):
                        if current_key:
                            embed_data[current_key] = " ".join(current_value)
                        current_key = "title"
                        current_value = [part[3:]]
                    elif part.startswith("dp:"):
                        if current_key:
                            embed_data[current_key] = " ".join(current_value)
                        current_key = "description"
                        current_value = [part[3:]]
                    elif part.startswith("ft:"):
                        if current_key:
                            embed_data[current_key] = " ".join(current_value)
                        current_key = "footer"
                        current_value = [part[3:]]
                    else:
                        current_value.append(part)
                
                if current_key:
                    embed_data[current_key] = " ".join(current_value)
                
                embed = discord.Embed(color=discord.Color.red())
                
                if "title" in embed_data:
                    embed.title = self.replace_variables(embed_data["title"], target, moderator, reason)
                if "description" in embed_data:
                    embed.description = self.replace_variables(embed_data["description"], target, moderator, reason)
                if "footer" in embed_data:
                    footer_text = self.replace_variables(embed_data["footer"], target, moderator, reason)
                    embed.set_footer(text=footer_text)
                    embed.timestamp = discord.utils.utcnow()
                
                return {"embed": embed}
            else:
                content = self.replace_variables(message, target, moderator, reason)
                return {"content": content}
        except Exception as e:
            print(f"Error parseando el mensaje de logs: {e}")
            return None

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        try:
            async for entry in guild.audit_logs(action=discord.AuditLogAction.ban, limit=1):
                if entry.target.id == user.id:
                    if entry.user.id == self.bot.user.id:
                        return
                    
                    await self.handle_ban_event(
                        guild=guild,
                        target=user,
                        moderator=entry.user,
                        reason=entry.reason,
                        source="manual"
                    )
                    break
        except Exception as e:
            print(f"Error en el evento on_member_ban: {e}")

async def setup(bot):
    await bot.add_cog(BanLogs(bot))