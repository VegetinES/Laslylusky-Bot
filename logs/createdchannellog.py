import discord
from discord.ext import commands
from database.get import get_specific_field
from logs.log_utils import LogParser

class CreatedChannelLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_parser = LogParser(bot)

    async def log_channel_create_event(self, channel):
        try:
            if not channel.guild:
                return
                
            guild_data = get_specific_field(channel.guild.id, "audit_logs")
            if not guild_data or "add_ch" not in guild_data:
                return
            
            add_channel_config = guild_data["add_ch"]
            
            is_activated = add_channel_config.get("activated")
            if isinstance(is_activated, str):
                is_activated = is_activated.lower() == "true"
            
            if not is_activated:
                return
                
            log_channel_id = add_channel_config.get("log_channel")
            if not log_channel_id or log_channel_id == 0:
                return
            
            log_channel = self.bot.get_channel(int(log_channel_id))
            if not log_channel:
                return
            
            category = channel.category
            
            message_data = add_channel_config.get("message", {})
            message_format = add_channel_config.get("add_ch_messages", "")
            
            if message_data and isinstance(message_data, dict):
                await self.log_parser.parse_and_send_log(
                    log_type="add_ch",
                    log_channel=log_channel,
                    message_format=message_data,
                    channel=channel,
                    category=category,
                    guild=channel.guild
                )
            elif message_format:
                await self.log_parser.parse_and_send_log(
                    log_type="add_ch",
                    log_channel=log_channel,
                    message_format=message_format,
                    channel=channel,
                    category=category,
                    guild=channel.guild
                )
            else:
                category_name = category.name if category else "Sin categoría"
                
                embed = discord.Embed(
                    title="Canal Creado",
                    description=f"**Canal:** {channel.mention} ({channel.id})\n**Categoría:** {category_name}",
                    color=discord.Color.green(),
                    timestamp=discord.utils.utcnow()
                )
                
                await log_channel.send(embed=embed)

        except Exception as e:
            print(f"Error en log_channel_create_event: {e}")

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        if isinstance(channel, (discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel)):
            await self.log_channel_create_event(channel)

async def setup(bot):
    await bot.add_cog(CreatedChannelLogs(bot))