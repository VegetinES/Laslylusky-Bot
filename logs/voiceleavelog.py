import discord
from discord.ext import commands
from database.get import get_specific_field
from logs.log_utils import LogParser

class VoiceLeaveLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_parser = LogParser(bot)

    async def log_voice_leave_event(self, member, voice_channel):
        try:
            if not member.guild:
                return
                
            guild_data = get_specific_field(member.guild.id, "audit_logs")
            if not guild_data or "vc_leave" not in guild_data:
                return
            
            vc_leave_config = guild_data["vc_leave"]
            
            is_activated = vc_leave_config.get("activated")
            if isinstance(is_activated, str):
                is_activated = is_activated.lower() == "true"
            
            if not is_activated:
                return
                
            log_channel_id = vc_leave_config.get("log_channel")
            if not log_channel_id or log_channel_id == 0:
                return
            
            log_channel = self.bot.get_channel(int(log_channel_id))
            if not log_channel:
                return
            
            message_data = vc_leave_config.get("message", {})
            message_format = vc_leave_config.get("vc_leave_messages", "")
            
            if message_data and isinstance(message_data, dict):
                await self.log_parser.parse_and_send_log(
                    log_type="vc_leave",
                    log_channel=log_channel,
                    message_format=message_data,
                    member=member,
                    voice_channel=voice_channel,
                    guild=member.guild
                )
            elif message_format:
                await self.log_parser.parse_and_send_log(
                    log_type="vc_leave",
                    log_channel=log_channel,
                    message_format=message_format,
                    member=member,
                    voice_channel=voice_channel,
                    guild=member.guild
                )
            else:
                embed = discord.Embed(
                    title="Usuario Desconectado de Canal de Voz",
                    description=f"**Usuario:** {member.mention} ({member.id})\n**Canal:** {voice_channel.mention}",
                    color=discord.Color.red(),
                    timestamp=discord.utils.utcnow()
                )
                
                await log_channel.send(embed=embed)

        except Exception as e:
            print(f"Error en log_voice_leave_event: {e}")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel != after.channel and before.channel is not None:
            await self.log_voice_leave_event(member, before.channel)

async def setup(bot):
    await bot.add_cog(VoiceLeaveLogs(bot))