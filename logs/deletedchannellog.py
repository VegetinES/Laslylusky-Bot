import discord
from discord.ext import commands
from database.get import get_specific_field
from logs.log_utils import LogParser

class DeletedChannelLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_parser = LogParser(bot)

    async def log_channel_delete_event(self, channel):
        try:
            if not channel.guild:
                return
                
            guild_data = get_specific_field(channel.guild.id, "audit_logs")
            if not guild_data or "del_ch" not in guild_data:
                return
            
            del_channel_config = guild_data["del_ch"]
            
            is_activated = del_channel_config.get("activated")
            if isinstance(is_activated, str):
                is_activated = is_activated.lower() == "true"
            
            if not is_activated:
                return
                
            log_channel_id = del_channel_config.get("log_channel")
            if not log_channel_id or log_channel_id == 0:
                return
            
            log_channel = self.bot.get_channel(int(log_channel_id))
            if not log_channel:
                return
            
            category = channel.category
            
            message_data = del_channel_config.get("message", {})
            message_format = del_channel_config.get("del_ch_messages", "")
            
            if message_data and isinstance(message_data, dict):
                await self.log_parser.parse_and_send_log(
                    log_type="del_ch",
                    log_channel=log_channel,
                    message_format=message_data,
                    channel=channel,
                    category=category,
                    guild=channel.guild
                )
            elif message_format:
                await self.log_parser.parse_and_send_log(
                    log_type="del_ch",
                    log_channel=log_channel,
                    message_format=message_format,
                    channel=channel,
                    category=category,
                    guild=channel.guild
                )
            else:
                category_name = category.name if category else "Sin categoría"
                
                embed = discord.Embed(
                    title="Canal Eliminado",
                    description=f"**Canal:** #{channel.name} ({channel.id})\n**Categoría:** {category_name}",
                    color=discord.Color.red(),
                    timestamp=discord.utils.utcnow()
                )
                
                await log_channel.send(embed=embed)

        except Exception as e:
            print(f"Error en log_channel_delete_event: {e}")

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        if isinstance(channel, (discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel)):
            await self.log_channel_delete_event(channel)

async def setup(bot):
    await bot.add_cog(DeletedChannelLogs(bot))