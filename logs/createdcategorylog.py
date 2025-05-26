import discord
from discord.ext import commands
from database.get import get_specific_field
from logs.log_utils import LogParser

class CreatedCategoryLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_parser = LogParser(bot)

    def format_permissions(self, category):
        try:
            formatted_perms = ""
            for target, overwrite in category.overwrites.items():
                target_name = target.name if hasattr(target, 'name') else str(target)
                formatted_perms += f"Permisos para `@{target_name}`:\n"

                has_specific_perms = False
                perms_text = ""
                
                for perm, value in overwrite:
                    if value is not None:
                        has_specific_perms = True
                        status = "✔️" if value else "❌"
                        perm_name = perm.replace('_', ' ').capitalize()
                        perms_text += f"- {perm_name} {status}\n"
                
                if has_specific_perms:
                    formatted_perms += perms_text
                else:
                    formatted_perms += "- Sin permisos específicos (heredados)\n"
                
                formatted_perms += "\n"
            
            if not formatted_perms:
                formatted_perms = "No hay permisos personalizados configurados."
            
            if len(formatted_perms) > 900:
                formatted_perms = formatted_perms[:900] + "..."
                
            return formatted_perms
        except Exception as e:
            print(f"Error al formatear permisos: {e}")
            return "Error al obtener los permisos de la categoría."

    async def log_category_create_event(self, category):
        try:
            if not category.guild:
                return
                
            guild_data = get_specific_field(category.guild.id, "audit_logs")
            if not guild_data or "add_cat" not in guild_data:
                return
            
            add_category_config = guild_data["add_cat"]
            
            is_activated = add_category_config.get("activated")
            if isinstance(is_activated, str):
                is_activated = is_activated.lower() == "true"
            
            if not is_activated:
                return
                
            log_channel_id = add_category_config.get("log_channel")
            if not log_channel_id or log_channel_id == 0:
                return
            
            log_channel = self.bot.get_channel(int(log_channel_id))
            if not log_channel:
                return
            
            perms = self.format_permissions(category)
            
            message_data = add_category_config.get("message", {})
            message_format = add_category_config.get("add_cat_messages", "")
            
            replacements = {
                "{category}": category.name,
                "{categoryid}": str(category.id),
                "{perms}": perms
            }
            
            if message_data and isinstance(message_data, dict):
                await self.log_parser.parse_and_send_log(
                    log_type="add_cat",
                    log_channel=log_channel,
                    message_format=message_data,
                    category=category,
                    guild=category.guild,
                    **replacements
                )
            elif message_format:
                await self.log_parser.parse_and_send_log(
                    log_type="add_cat",
                    log_channel=log_channel,
                    message_format=message_format,
                    category=category,
                    guild=category.guild,
                    **replacements
                )
            else:
                embed = discord.Embed(
                    title="Categoría Creada",
                    description=f"**Categoría:** {category.name} ({category.id})",
                    color=discord.Color.green(),
                    timestamp=discord.utils.utcnow()
                )
                
                embed.add_field(
                    name="Permisos",
                    value=perms,
                    inline=False
                )
                
                await log_channel.send(embed=embed)

        except Exception as e:
            print(f"Error en log_category_create_event: {e}")

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        if isinstance(channel, discord.CategoryChannel):
            await self.log_category_create_event(channel)

async def setup(bot):
    await bot.add_cog(CreatedCategoryLogs(bot))