import discord
from discord.ext import commands
from database.get import get_specific_field
import asyncio

async def send_unban_log(bot, guild: discord.Guild, target: discord.User, moderator: discord.Member = None, source: str = "manual"):
    cog = bot.get_cog('UnbanLogs')
    if cog:
        await cog.handle_unban_event(guild, target, moderator, source)

class UnbanLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.recent_unbans = {}

    async def _clear_recent_unban(self, guild_id: int, user_id: int):
        await asyncio.sleep(5)
        if guild_id in self.recent_unbans and user_id in self.recent_unbans[guild_id]:
            del self.recent_unbans[guild_id][user_id]

    async def handle_unban_event(self, guild: discord.Guild, target: discord.User, moderator: discord.Member = None, source: str = "manual"):
        if guild.id not in self.recent_unbans:
            self.recent_unbans[guild.id] = {}

        if source == "command":
            self.recent_unbans[guild.id][target.id] = True
            await self.log_unban_event(guild, target, moderator, source)
            self.bot.loop.create_task(self._clear_recent_unban(guild.id, target.id))
            return

        if target.id in self.recent_unbans.get(guild.id, {}):
            return

        await self.log_unban_event(guild, target, moderator, source)

    async def log_unban_event(self, guild: discord.Guild, target: discord.User, moderator: discord.Member = None, source: str = "manual"):
        try:
            guild_data = get_specific_field(guild.id, "audit_logs")
            if not guild_data or "unban" not in guild_data:
                return
            
            unban_config = guild_data["unban"]
            
            is_activated = unban_config.get("activated")
            if isinstance(is_activated, str):
                is_activated = is_activated.lower() == "true"
            
            if not is_activated:
                return
                
            log_channel_id = unban_config.get("log_channel")
            if not log_channel_id or log_channel_id == 0:
                return
            
            log_channel = self.bot.get_channel(int(log_channel_id))
            if not log_channel:
                return
            
            message_format = unban_config.get("unban_messages", "")
            if not message_format:
                return

            message_data = await self.parse_log_message(message_format, target, moderator)
            if message_data:
                if "embed" in message_data:
                    await log_channel.send(embed=message_data["embed"])
                else:
                    await log_channel.send(message_data["content"])

        except Exception as e:
            print(f"Error in log_unban_event: {e}")

    async def parse_log_message(self, message: str, target: discord.User, moderator: discord.Member = None):
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
                
                embed = discord.Embed(color=discord.Color.green())
                
                if "title" in embed_data:
                    embed.title = embed_data["title"]
                if "description" in embed_data:
                    description = embed_data["description"]
                    description = description.replace("{user}", str(target))
                    description = description.replace("{user_id}", str(target.id))
                    if moderator:
                        description = description.replace("{mod}", str(moderator))
                        description = description.replace("{mod_id}", str(moderator.id))
                    embed.description = description
                if "footer" in embed_data:
                    footer = embed_data["footer"]
                    footer = footer.replace("{user}", str(target))
                    footer = footer.replace("{user_id}", str(target.id))
                    if moderator:
                        footer = footer.replace("{mod}", str(moderator))
                        footer = footer.replace("{mod_id}", str(moderator.id))
                    embed.set_footer(text=footer)
                
                embed.timestamp = discord.utils.utcnow()
                return {"embed": embed}
            else:
                content = message
                content = content.replace("{user}", str(target))
                content = content.replace("{user_id}", str(target.id))
                if moderator:
                    content = content.replace("{mod}", str(moderator))
                    content = content.replace("{mod_id}", str(moderator.id))
                return {"content": content}

        except Exception as e:
            print(f"Error parsing log message: {e}")
            return None

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        try:
            async for entry in guild.audit_logs(action=discord.AuditLogAction.unban, limit=1):
                if entry.target.id == user.id:
                    if entry.user.id == self.bot.user.id:
                        return
                    
                    await self.handle_unban_event(
                        guild=guild,
                        target=user,
                        moderator=entry.user,
                        source="manual"
                    )
                    break
        except Exception as e:
            print(f"Error in on_member_unban event: {e}")

async def setup(bot):
    await bot.add_cog(UnbanLogs(bot))