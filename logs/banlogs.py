import discord
from discord.ext import commands
from database.get import get_specific_field
import asyncio
from logs.log_utils import LogParser

async def send_ban_log(bot, guild: discord.Guild, target: discord.User, moderator: discord.User = None, reason: str = None, source: str = "manual"):
    cog = bot.get_cog('BanLogs')
    if cog:
        await cog.handle_ban_event(guild, target, moderator, reason, source)

class BanLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.recent_bans = {}
        self.log_parser = LogParser(bot)

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

            message_data = ban_config.get("message", {})
            message_format = ban_config.get("ban_messages", "")
            
            if message_data and isinstance(message_data, dict):
                await self.log_parser.parse_and_send_log(
                    log_type="ban",
                    log_channel=log_channel,
                    message_format=message_data,
                    target=target,
                    moderator=moderator,
                    reason=reason,
                    guild=guild
                )
            elif message_format:
                await self.log_parser.parse_and_send_log(
                    log_type="ban",
                    log_channel=log_channel,
                    message_format=message_format,
                    target=target,
                    moderator=moderator,
                    reason=reason,
                    guild=guild
                )
            else:
                embed = discord.Embed(
                    title="Usuario Baneado",
                    description=f"**Usuario:** {target.mention} ({target.id})\n**Razón:** {reason or 'No especificada'}",
                    color=discord.Color.red(),
                    timestamp=discord.utils.utcnow()
                )
                if moderator:
                    embed.add_field(name="Moderador", value=f"{moderator.mention} ({moderator.id})")
                
                await log_channel.send(embed=embed)

        except Exception as e:
            print(f"Error en log_ban_event: {e}")

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