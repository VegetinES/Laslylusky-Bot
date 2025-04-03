import discord
from discord.ext import commands
from database.get import get_specific_field
from logs.log_utils import LogParser

class EnterLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_parser = LogParser(bot)

    async def log_enter_event(self, member: discord.Member):
        try:
            guild_data = get_specific_field(member.guild.id, "audit_logs")
            if not guild_data or "enter" not in guild_data:
                return
            
            enter_config = guild_data["enter"]
            
            is_activated = enter_config.get("activated")
            if isinstance(is_activated, str):
                is_activated = is_activated.lower() == "true"
            
            if not is_activated:
                return
                
            log_channel_id = enter_config.get("log_channel")
            if not log_channel_id or log_channel_id == 0:
                return
            
            log_channel = self.bot.get_channel(int(log_channel_id))
            if not log_channel:
                return
            
            message_data = enter_config.get("message", {})
            message_format = enter_config.get("enter_messages", "")
            
            accage = int(member.created_at.timestamp())
            
            if message_data and isinstance(message_data, dict):
                await self.log_parser.parse_and_send_log(
                    log_type="enter",
                    log_channel=log_channel,
                    message_format=message_data,
                    member=member,
                    accage=accage,
                    guild=member.guild
                )
            elif message_format:
                await self.log_parser.parse_and_send_log(
                    log_type="enter",
                    log_channel=log_channel,
                    message_format=message_format,
                    member=member,
                    accage=accage,
                    guild=member.guild
                )
            else:
                embed = discord.Embed(
                    title="Usuario se unió al servidor",
                    description=f"**Usuario:** {member.mention} ({member.id})\n**Cuenta creada:** <t:{int(member.created_at.timestamp())}:f>",
                    color=discord.Color.green(),
                    timestamp=discord.utils.utcnow()
                )
                
                await log_channel.send(embed=embed)

        except Exception as e:
            print(f"Error en log_enter_event: {e}")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        await self.log_enter_event(member)

async def setup(bot):
    await bot.add_cog(EnterLogs(bot))