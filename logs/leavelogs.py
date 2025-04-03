import discord
from discord.ext import commands
from database.get import get_specific_field
from logs.log_utils import LogParser
import time

class LeaveLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_parser = LogParser(bot)

    async def log_leave_event(self, member: discord.Member):
        try:
            guild_data = get_specific_field(member.guild.id, "audit_logs")
            if not guild_data or "leave" not in guild_data:
                return
            
            leave_config = guild_data["leave"]
            
            is_activated = leave_config.get("activated")
            if isinstance(is_activated, str):
                is_activated = is_activated.lower() == "true"
            
            if not is_activated:
                return
                
            log_channel_id = leave_config.get("log_channel")
            if not log_channel_id or log_channel_id == 0:
                return
            
            log_channel = self.bot.get_channel(int(log_channel_id))
            if not log_channel:
                return
            
            message_data = leave_config.get("message", {})
            message_format = leave_config.get("leave_messages", "")
            
            joined_at_ts = int(member.joined_at.timestamp()) if member.joined_at else int(time.time())
            created_at_ts = int(member.created_at.timestamp())
            
            if message_data and isinstance(message_data, dict):
                await self.log_parser.parse_and_send_log(
                    log_type="leave",
                    log_channel=log_channel,
                    message_format=message_data,
                    member=member,
                    guild=member.guild
                )
            elif message_format:
                await self.log_parser.parse_and_send_log(
                    log_type="leave",
                    log_channel=log_channel,
                    message_format=message_format,
                    member=member,
                    guild=member.guild
                )
            else:
                embed = discord.Embed(
                    title="Usuario abandonó el servidor",
                    description=(
                        f"**Usuario:** {member.mention} ({member.id})\n"
                        f"**Cuenta creada:** <t:{created_at_ts}:f>\n"
                        f"**Tiempo en el servidor:** <t:{joined_at_ts}:R>"
                    ),
                    color=discord.Color.red(),
                    timestamp=discord.utils.utcnow()
                )
                
                await log_channel.send(embed=embed)

        except Exception as e:
            print(f"Error en log_leave_event: {e}")

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        await self.log_leave_event(member)

async def setup(bot):
    await bot.add_cog(LeaveLogs(bot))