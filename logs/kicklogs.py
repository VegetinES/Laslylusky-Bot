import discord
from discord.ext import commands
from database.get import get_specific_field
import asyncio

async def send_kick_log(bot, guild: discord.Guild, target: discord.User, moderator: discord.User = None, reason: str = None, source: str = "manual"):
    cog = bot.get_cog('KickLogs')
    if cog:
        await cog.handle_kick_event(guild, target, moderator, reason, source)

class KickLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.recent_kicks = {}

    async def _clear_recent_kick(self, guild_id: int, user_id: int):
        await asyncio.sleep(5)
        if guild_id in self.recent_kicks and user_id in self.recent_kicks[guild_id]:
            del self.recent_kicks[guild_id][user_id]

    async def handle_kick_event(self, guild: discord.Guild, target: discord.User, moderator: discord.User = None, reason: str = None, source: str = "manual"):
        if guild.id not in self.recent_kicks:
            self.recent_kicks[guild.id] = {}

        if source == "command":
            self.recent_kicks[guild.id][target.id] = True
            await self.log_kick_event(guild, target, moderator, reason, source)
            self.bot.loop.create_task(self._clear_recent_kick(guild.id, target.id))
            return

        if target.id in self.recent_kicks.get(guild.id, {}):
            return

        await self.log_kick_event(guild, target, moderator, reason, source)

    def get_replacements(self, target: discord.User, moderator: discord.User = None, reason: str = None):
        replacements = {
            "{usertag}": str(target),
            "{user}": target.mention,
            "{userid}": str(target.id),
        }
        
        if moderator:
            replacements.update({
                "{modtag}": str(moderator),
                "{mod}": moderator.mention,
                "{modid}": str(moderator.id),
            })
        
        if reason:
            replacements.update({
                "{reason}": str(reason),
            })
            
        return replacements
    
    def replace_variables(self, text: str, replacements: dict) -> str:
        result = text
        for key, value in replacements.items():
            result = result.replace(key, value)
        return result

    async def log_kick_event(self, guild: discord.Guild, target: discord.User, moderator: discord.User = None, reason: str = None, source: str = "manual"):
        try:
            guild_data = get_specific_field(guild.id, "audit_logs")
            if not guild_data or "kick" not in guild_data:
                return
            
            kick_config = guild_data["kick"]
            
            is_activated = kick_config.get("activated")
            if isinstance(is_activated, str):
                is_activated = is_activated.lower() == "true"
            
            if not is_activated:
                return
                
            log_channel_id = kick_config.get("log_channel")
            if not log_channel_id or log_channel_id == 0:
                return
            
            log_channel = self.bot.get_channel(int(log_channel_id))
            if not log_channel:
                return
            
            message_format = kick_config.get("kick_messages", "")
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
            print(f"Error en log_kick_event: {e}")

    async def parse_log_message(self, message: str, target: discord.User, moderator: discord.User = None, reason: str = None):
        try:
            replacements = self.get_replacements(target, moderator, reason)
            
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
                
                embed = discord.Embed(color=discord.Color.orange())
                
                if "title" in embed_data:
                    embed.title = self.replace_variables(embed_data["title"], replacements)
                    
                if "description" in embed_data:
                    embed.description = self.replace_variables(embed_data["description"], replacements)
                    
                if "footer" in embed_data:
                    footer_text = self.replace_variables(embed_data["footer"], replacements)
                    embed.set_footer(text=footer_text)
                    embed.timestamp = discord.utils.utcnow()
                
                return {"embed": embed}
            else:
                content = self.replace_variables(message, replacements)
                return {"content": content}
                
        except Exception as e:
            print(f"Error parseando el mensaje de log: {e}")
            return None

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        try:
            async for entry in member.guild.audit_logs(action=discord.AuditLogAction.kick, limit=1):
                if entry.target.id == member.id:
                    if entry.user.id == self.bot.user.id:
                        return
                    
                    await self.handle_kick_event(
                        guild=member.guild,
                        target=member,
                        moderator=entry.user,
                        reason=entry.reason,
                        source="manual"
                    )
                    break
        except Exception as e:
            print(f"Error en el evento on_member_remove: {e}")

async def setup(bot):
    await bot.add_cog(KickLogs(bot))