import discord
from discord.ext import commands
from database.get import get_specific_field
from logs.log_utils import LogParser

class WarnLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_parser = LogParser(bot)

    async def log_warn_event(self, guild_id, user_id, user_mention, user_tag, reason, mod_id, mod_mention, mod_tag, warn_id):
        try:
            guild = self.bot.get_guild(guild_id)
            if not guild:
                return
                
            guild_data = get_specific_field(guild_id, "audit_logs")
            if not guild_data or "warn" not in guild_data:
                return
            
            warn_config = guild_data["warn"]
            
            is_activated = warn_config.get("activated")
            if isinstance(is_activated, str):
                is_activated = is_activated.lower() == "true"
            
            if not is_activated:
                return
                
            log_channel_id = warn_config.get("log_channel")
            if not log_channel_id or log_channel_id == 0:
                return
            
            log_channel = self.bot.get_channel(int(log_channel_id))
            if not log_channel:
                return

            message_data = warn_config.get("message", {})
            message_format = warn_config.get("warn_messages", "")
            
            if message_data and isinstance(message_data, dict):
                await self.log_parser.parse_and_send_log(
                    log_type="warn",
                    log_channel=log_channel,
                    message_format=message_data,
                    user_id=user_id,
                    user_mention=user_mention,
                    user_tag=user_tag,
                    reason=reason,
                    mod_id=mod_id,
                    mod_mention=mod_mention,
                    mod_tag=mod_tag,
                    warn_id=warn_id,
                    guild=guild
                )
            elif message_format:
                await self.log_parser.parse_and_send_log(
                    log_type="warn",
                    log_channel=log_channel,
                    message_format=message_format,
                    user_id=user_id,
                    user_mention=user_mention,
                    user_tag=user_tag,
                    reason=reason,
                    mod_id=mod_id,
                    mod_mention=mod_mention,
                    mod_tag=mod_tag,
                    warn_id=warn_id,
                    guild=guild
                )
            else:
                embed = discord.Embed(
                    title="Usuario Advertido",
                    description=f"**Usuario:** {user_mention} ({user_id})\n**Advertencia ID:** {warn_id}\n**Razón:** {reason or 'No especificada'}",
                    color=discord.Color.gold(),
                    timestamp=discord.utils.utcnow()
                )
                if mod_id:
                    embed.add_field(name="Moderador", value=f"{mod_mention} ({mod_id})")
                
                await log_channel.send(embed=embed)

        except Exception as e:
            print(f"Error en log_warn_event: {e}")

    @commands.Cog.listener()
    async def on_warn(self, guild_id, user_id, user_mention, user_tag, reason, mod_id, mod_mention, mod_tag, warn_id):
        await self.log_warn_event(guild_id, user_id, user_mention, user_tag, reason, mod_id, mod_mention, mod_tag, warn_id)

async def setup(bot):
    await bot.add_cog(WarnLogs(bot))