import discord
from .configlogs_constants import LOG_TYPES, COLORS

async def create_preview(log_type, message_data, guild):
    try:
        if not message_data or not isinstance(message_data, dict):
            return {
                "content": f"**Configuración de {LOG_TYPES[log_type]['name']}**\n**No hay configuración de mensaje**"
            }
        
        if message_data.get("embed", False):
            color_value = message_data.get("color", "default")
            color_tuple = COLORS.get(color_value, COLORS["default"])
            
            embed = discord.Embed(
                title=message_data.get("title", ""),
                description=message_data.get("description", ""),
                color=color_tuple[0]
            )
            
            if message_data.get("footer"):
                embed.set_footer(text=message_data["footer"])
            
            if message_data.get("thumbnail", {}).get("has", False):
                thumbnail_param = message_data["thumbnail"].get("param", "")
                if thumbnail_param:
                    if thumbnail_param == "{servericon}" and guild.icon:
                        embed.set_thumbnail(url=guild.icon.url)
                    elif thumbnail_param == "{useravatar}":
                        embed.set_thumbnail(url=guild.me.avatar.url if guild.me.avatar else None)
                    else:
                        embed.set_thumbnail(url=thumbnail_param)

            if message_data.get("image", {}).get("has", False):
                image_param = message_data["image"].get("param", "")
                if image_param:
                    if image_param == "{servericon}" and guild.icon:
                        embed.set_image(url=guild.icon.url)
                    elif image_param == "{useravatar}":
                        embed.set_image(url=guild.me.avatar.url if guild.me.avatar else None)
                    else:
                        embed.set_image(url=image_param)

            if message_data.get("fields"):
                sorted_fields = sorted(message_data["fields"].items(), key=lambda x: int(x[0]))
                for field_id, field_data in sorted_fields:
                    embed.add_field(
                        name=field_data.get("name", ""),
                        value=field_data.get("value", ""),
                        inline=field_data.get("inline", False)
                    )

            content = f"**Configuración de {LOG_TYPES[log_type]['name']}**\n"
            content += "**Tipo de mensaje:** Embed\n"
            content += f"**Color:** {COLORS.get(color_value, COLORS['default'])[1]} {COLORS.get(color_value, COLORS['default'])[2]}\n"
            
            if message_data.get("thumbnail", {}).get("has", False):
                content += f"**Thumbnail:** Activado\n"
            else:
                content += f"**Thumbnail:** Desactivado\n"
                
            if message_data.get("image", {}).get("has", False):
                content += f"**Imagen:** Activada\n"
            else:
                content += f"**Imagen:** Desactivada\n"
                
            fields_count = len(message_data.get("fields", {}))
            content += f"**Campos:** {fields_count}"
            
            return {
                "content": content,
                "embed": embed
            }
        
        else:
            message = message_data.get("message", "")
            if not message:
                return {
                    "content": f"**Configuración de {LOG_TYPES[log_type]['name']}**\n**Tipo de mensaje:** Normal\n**No hay mensaje configurado**"
                }

            display_message = message[:100] + ('...' if len(message) > 100 else '')
            content = f"**Configuración de {LOG_TYPES[log_type]['name']}**\n"
            content += "**Tipo de mensaje:** Normal\n"
            content += f"**Mensaje configurado:**\n```\n{display_message}\n```"
            
            return {"content": content}
            
    except Exception as e:
        print(f"Error en create_preview: {e}")
        return {"content": f"Error al generar vista previa: {str(e)}"}