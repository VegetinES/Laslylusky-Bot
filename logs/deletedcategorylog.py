import discord
from discord.ext import commands
from database.get import get_specific_field
from logs.log_utils import LogParser

class DeletedCategoryLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_parser = LogParser(bot)

    async def log_category_delete_event(self, category):
        try:
            if not category.guild:
                return
                
            guild_data = get_specific_field(category.guild.id, "audit_logs")
            if not guild_data or "del_cat" not in guild_data:
                return
            
            del_category_config = guild_data["del_cat"]
            
            is_activated = del_category_config.get("activated")
            if isinstance(is_activated, str):
                is_activated = is_activated.lower() == "true"
            
            if not is_activated:
                return
                
            log_channel_id = del_category_config.get("log_channel")
            if not log_channel_id or log_channel_id == 0:
                return
            
            log_channel = self.bot.get_channel(int(log_channel_id))
            if not log_channel:
                return
            
            message_data = del_category_config.get("message", {})
            message_format = del_category_config.get("del_cat_messages", "")
            
            replacements = {
                "{category}": category.name,
                "{categoryid}": str(category.id)
            }
            
            if message_data and isinstance(message_data, dict):
                await self.log_parser.parse_and_send_log(
                    log_type="del_cat",
                    log_channel=log_channel,
                    message_format=message_data,
                    category=category,
                    guild=category.guild,
                    **replacements
                )
            elif message_format:
                await self.log_parser.parse_and_send_log(
                    log_type="del_cat",
                    log_channel=log_channel,
                    message_format=message_format,
                    category=category,
                    guild=category.guild,
                    **replacements
                )
            else:
                embed = discord.Embed(
                    title="Categoría Eliminada",
                    description=f"**Categoría:** {category.name} ({category.id})",
                    color=discord.Color.red(),
                    timestamp=discord.utils.utcnow()
                )
                
                await log_channel.send(embed=embed)

        except Exception as e:
            print(f"Error en log_category_delete_event: {e}")

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        if isinstance(channel, discord.CategoryChannel):
            await self.log_category_delete_event(channel)

async def setup(bot):
    await bot.add_cog(DeletedCategoryLogs(bot))