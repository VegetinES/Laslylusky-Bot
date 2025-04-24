import discord
from ...utils.preview import generate_preview as original_generate_preview
from ...constants import COLORS

async def generate_preview(message_type, message_config, guild):
    try:
        if not message_config or not isinstance(message_config, dict):
            return {
                "content": f"**Configuración de {message_type}**\n\nNo hay configuración"
            }
            
        result = {}
        content = ""
        
        if "VIEW_MODE" not in message_config:
            if message_type == "open_message":
                buttons_preview = ""
                if message_config.get("buttons"):
                    for button in message_config.get("buttons", []):
                        emoji = button.get("emoji", "")
                        label = button.get("label", "Abrir Ticket")
                        buttons_preview += f"[Botón: {emoji} {label}]\n"
                content = buttons_preview
            elif message_type.startswith("opened_message"):
                content = "[Botón: 🔒 Cerrar Ticket] [Botón: ➕ Añadir Usuario] [Botón: ➖ Eliminar Usuario]\n"
        
        if "VIEW_MODE" in message_config:
            if message_config.get("plain_message"):
                content = message_config.get("plain_message")
            else:
                content = ""
        elif message_config.get("plain_message"):
            content += message_config.get("plain_message")
        
        result["content"] = content
        
        if message_config.get("embed"):
            color_name = message_config.get("color", "default") 
            color_value = COLORS.get(color_name, COLORS["default"])[0] if color_name in COLORS else 0x3498db
            
            embed = discord.Embed(
                title=message_config.get("title", ""),
                description=message_config.get("description", ""),
                color=color_value
            )
            
            if message_config.get("footer"):
                embed.set_footer(text=message_config.get("footer"))
            
            if message_config.get("image", {}).get("enabled") and message_config.get("image", {}).get("url"):
                embed.set_image(url=message_config.get("image", {}).get("url") or "https://placehold.co/600x400?text=Imagen")
            
            if message_config.get("thumbnail", {}).get("enabled") and message_config.get("thumbnail", {}).get("url"):
                embed.set_thumbnail(url=message_config.get("thumbnail", {}).get("url") or "https://placehold.co/150x150?text=Thumbnail")
            
            if message_config.get("fields"):
                for field in message_config.get("fields", []):
                    embed.add_field(
                        name=field.get("name", ""),
                        value=field.get("value", ""),
                        inline=field.get("inline", False)
                    )
            
            result["embed"] = embed
        
        return result
    except Exception as e:
        print(f"Error al generar vista previa: {e}")
        return {
            "content": f"**Error al generar vista previa**: {str(e)}"
        }