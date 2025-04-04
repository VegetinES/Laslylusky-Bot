import discord
import re
from datetime import datetime
import traceback

PREVIEW_AVATAR_URL = "https://cdn.discordapp.com/embed/avatars/0.png"
PREVIEW_SERVER_ICON = "https://cdn.discordapp.com/embed/avatars/1.png"

PREVIEW_PARAMS = {
    "ban": {
        "{userid}": "123456789012345678",
        "{usertag}": "usuario",
        "{user}": "@Usuario",
        "{modid}": "987654321098765432",
        "{modtag}": "moderador",
        "{mod}": "@Moderador",
        "{reason}": "Ejemplo de razón de baneo"
    },
    "kick": {
        "{userid}": "123456789012345678",
        "{usertag}": "usuario",
        "{user}": "@Usuario",
        "{modid}": "987654321098765432",
        "{modtag}": "moderador",
        "{mod}": "@Moderador",
        "{reason}": "Ejemplo de razón de expulsión"
    },
    "unban": {
        "{userid}": "123456789012345678",
        "{usertag}": "usuario",
        "{modid}": "987654321098765432",
        "{modtag}": "moderador",
        "{mod}": "@Moderador"
    },
    "enter": {
        "{userid}": "123456789012345678",
        "{usertag}": "usuario",
        "{user}": "@Usuario",
        "{accage}": "3 días",
        "{acc_age}": "<t:1712345678:f>"
    },
    "leave": {
        "{userid}": "123456789012345678",
        "{usertag}": "usuario",
        "{acc_age}": "<t:1712345678:f>",
        "{server_age}": "<t:1712355678:R>"
    },
    "del_msg": {
        "{del_msg}": "Este es un ejemplo de mensaje eliminado",
        "{usertag}": "usuario",
        "{userid}": "123456789012345678",
        "{user}": "@Usuario",
        "{channel}": "#canal-general",
        "{channelid}": "123456789012345679",
        "{attached}": "No hay adjuntos"
    },
    "edited_msg": {
        "{user}": "@Usuario",
        "{userid}": "123456789012345678",
        "{usertag}": "usuario",
        "{channel}": "#canal-general",
        "{channelid}": "123456789012345679",
        "{old_msg}": "Mensaje original",
        "{new_msg}": "Mensaje editado",
        "{attached}": "No hay adjuntos"
    },
    "warn": {
        "{user}": "@Usuario",
        "{userid}": "123456789012345678",
        "{usertag}": "usuario",
        "{reason}": "Ejemplo de razón de advertencia",
        "{mod}": "@Moderador",
        "{modtag}": "moderador",
        "{modid}": "987654321098765432",
        "{warnid}": "1"
    },
    "unwarn": {
        "{user}": "@Usuario",
        "{userid}": "123456789012345678",
        "{usertag}": "usuario",
        "{reason}": "Ejemplo de razón de eliminación de advertencia",
        "{mod}": "@Moderador",
        "{modtag}": "moderador",
        "{modid}": "987654321098765432",
        "{warnid}": "1"
    }
}

COLORS = {
    "default": [0x3498db, "Azul predeterminado"],
    "blue": [0x3498db, "Azul"],
    "red": [0xff0000, "Rojo"],
    "green": [0x2ecc71, "Verde"],
    "orange": [0xe67e22, "Naranja"],
    "purple": [0x9b59b6, "Púrpura"],
    "yellow": [0xf1c40f, "Amarillo"],
    "gray": [0x95a5a6, "Gris"],
    "black": [0x000000, "Negro"],
    "white": [0xffffff, "Blanco"]
}

def is_valid_url(url):
    if not url:
        return False
        
    url_pattern = re.compile(
        r'^(https?://)?'
        r'([a-zA-Z0-9]+\.)+[a-zA-Z]{2,}'
        r'(/[a-zA-Z0-9._~:/?#[\]@!$&\'()*+,;=]*)?'
        r'$'
    )
    return bool(url_pattern.match(url))

def replace_variables(text, replacements):
    if not text:
        return ""
        
    result = text.replace(r"{\n}", "\n").replace("{\\n}", "\n")
    
    for key, value in replacements.items():
        result = result.replace(key, str(value))
        
    return result

async def create_preview(log_type, message_config, guild):
    try:
        replacements = PREVIEW_PARAMS.get(log_type, {})
        
        if not message_config:
            return {
                "content": "No hay configuración de mensaje para mostrar una vista previa."
            }
        
        if message_config.get("embed", False):
            color_name = message_config.get("color", "default")
            try:
                color_value = COLORS.get(color_name, COLORS["default"])[0] if color_name in COLORS else 0x3498db
            except (KeyError, IndexError, TypeError):
                color_value = 0x3498db
            
            embed = discord.Embed(
                title=replace_variables(message_config.get("title", ""), replacements),
                description=replace_variables(message_config.get("description", ""), replacements),
                color=color_value
            )

            if message_config.get("footer"):
                footer_text = replace_variables(message_config["footer"], replacements)
                embed.set_footer(text=footer_text)

            if message_config.get("thumbnail", {}).get("has", False):
                thumbnail_param = message_config["thumbnail"].get("param", "")
                
                if thumbnail_param == "{servericon}":
                    embed.set_thumbnail(url=PREVIEW_SERVER_ICON)
                elif thumbnail_param == "{useravatar}":
                    embed.set_thumbnail(url=PREVIEW_AVATAR_URL)
                elif is_valid_url(thumbnail_param):
                    embed.set_thumbnail(url=thumbnail_param)

            if message_config.get("image", {}).get("has", False):
                image_param = message_config["image"].get("param", "")
                
                if image_param == "{servericon}":
                    embed.set_image(url=PREVIEW_SERVER_ICON)
                elif image_param == "{useravatar}":
                    embed.set_image(url=PREVIEW_AVATAR_URL)
                elif is_valid_url(image_param):
                    embed.set_image(url=image_param)

            if "fields" in message_config:
                fields_data = message_config["fields"]

                if isinstance(fields_data, list):
                    for i, field_data in enumerate(fields_data):
                        try:
                            if field_data is None or not isinstance(field_data, dict):
                                continue
                            
                            field_name = replace_variables(field_data.get("name", ""), replacements)
                            field_value = replace_variables(field_data.get("value", ""), replacements)

                            if not field_name and not field_value:
                                continue

                            if not field_name:
                                field_name = "\u200b"
                            if not field_value:
                                field_value = "\u200b"
                            
                            field_inline = field_data.get("inline", False)
                            if isinstance(field_inline, str):
                                field_inline = field_inline.lower() in ["true", "yes", "1", "si", "sí"]
                            
                            embed.add_field(
                                name=field_name,
                                value=field_value,
                                inline=bool(field_inline)
                            )
                        except Exception as e:
                            print(f"Error procesando field {i}: {e}")

                elif isinstance(fields_data, dict):
                    sorted_fields = []
                    for field_id, field_data in fields_data.items():
                        try:
                            field_num = int(field_id) if field_id.isdigit() else float('inf')
                            
                            if not isinstance(field_data, dict):
                                continue
                            
                            field_name = replace_variables(field_data.get("name", ""), replacements)
                            field_value = replace_variables(field_data.get("value", ""), replacements)
                            
                            if not field_name and not field_value:
                                continue
                            
                            if not field_name:
                                field_name = "\u200b"
                            if not field_value:
                                field_value = "\u200b"

                            field_inline = field_data.get("inline", False)
                            if isinstance(field_inline, str):
                                field_inline = field_inline.lower() in ["true", "yes", "1", "si", "sí"]
                            
                            sorted_fields.append((field_num, {
                                "name": field_name,
                                "value": field_value,
                                "inline": bool(field_inline)
                            }))
                        except Exception as e:
                            print(f"Error procesando field {field_id}: {e}")
                    
                    sorted_fields.sort(key=lambda x: x[0])
                    
                    for field_num, field_attrs in sorted_fields:
                        try:
                            embed.add_field(
                                name=field_attrs["name"],
                                value=field_attrs["value"],
                                inline=field_attrs["inline"]
                            )
                        except Exception as e:
                            print(f"Error al añadir field al embed: {e}")
            
            embed.timestamp = discord.utils.utcnow()
            
            return {
                "embed": embed
            }
        else:
            message_text = message_config.get("message", "")
            if not message_text:
                return {
                    "content": "No hay mensaje configurado para mostrar una vista previa."
                }

            content = replace_variables(message_text, replacements)
            return {
                "content": content
            }
    except Exception as e:
        traceback_str = traceback.format_exc()
        print(f"Error en create_preview: {e}\n{traceback_str}")
        return {
            "content": f"Error al generar la vista previa: {e}"
        }