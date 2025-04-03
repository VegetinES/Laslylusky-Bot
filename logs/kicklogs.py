import discord
from discord.ext import commands
from database.get import get_specific_field
import asyncio
from logs.log_utils import LogParser

async def send_kick_log(bot, guild: discord.Guild, target: discord.User, moderator: discord.User = None, reason: str = None, source: str = "manual"):
    cog = bot.get_cog('KickLogs')
    if cog:
        await cog.handle_kick_event(guild, target, moderator, reason, source)

class KickLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.recent_kicks = {}
        self.log_parser = LogParser(bot)

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
            
            message_data = kick_config.get("message", {})
            message_format = kick_config.get("kick_messages", "")
            
            if message_data and isinstance(message_data, dict):
                await self.log_parser.parse_and_send_log(
                    log_type="kick",
                    log_channel=log_channel,
                    message_format=message_data,
                    target=target,
                    moderator=moderator,
                    reason=reason,
                    guild=guild
                )
            elif message_format:
                await self.log_parser.parse_and_send_log(
                    log_type="kick",
                    log_channel=log_channel,
                    message_format=message_format,
                    target=target,
                    moderator=moderator,
                    reason=reason,
                    guild=guild
                )
            else:
                embed = discord.Embed(
                    title="Usuario Expulsado",
                    description=f"**Usuario:** {target.mention} ({target.id})\n**Razón:** {reason or 'No especificada'}",
                    color=discord.Color.orange(),
                    timestamp=discord.utils.utcnow()
                )
                if moderator:
                    embed.add_field(name="Moderador", value=f"{moderator.mention} ({moderator.id})")
                
                await log_channel.send(embed=embed)

        except Exception as e:
            print(f"Error en log_kick_event: {e}")

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