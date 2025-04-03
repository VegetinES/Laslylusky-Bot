import discord
from discord.ext import commands
from database.get import get_specific_field
import asyncio
from logs.log_utils import LogParser

async def send_unban_log(bot, guild: discord.Guild, target: discord.User, moderator: discord.Member = None, source: str = "manual"):
    cog = bot.get_cog('UnbanLogs')
    if cog:
        await cog.handle_unban_event(guild, target, moderator, source)

class UnbanLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.recent_unbans = {}
        self.log_parser = LogParser(bot)

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
            
            message_data = unban_config.get("message", {})
            message_format = unban_config.get("unban_messages", "")
            
            if message_data and isinstance(message_data, dict):
                await self.log_parser.parse_and_send_log(
                    log_type="unban",
                    log_channel=log_channel,
                    message_format=message_data,
                    target=target,
                    moderator=moderator,
                    guild=guild
                )
            elif message_format:
                await self.log_parser.parse_and_send_log(
                    log_type="unban",
                    log_channel=log_channel,
                    message_format=message_format,
                    target=target,
                    moderator=moderator,
                    guild=guild
                )
            else:
                embed = discord.Embed(
                    title="Usuario Desbaneado",
                    description=f"**Usuario:** {target.mention} ({target.id})",
                    color=discord.Color.green(),
                    timestamp=discord.utils.utcnow()
                )
                if moderator:
                    embed.add_field(name="Moderador", value=f"{moderator.mention} ({moderator.id})")
                
                await log_channel.send(embed=embed)

        except Exception as e:
            print(f"Error in log_unban_event: {e}")

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