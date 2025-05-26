import discord
import re
from datetime import datetime
import traceback

from .configlogs_constants import LOG_TYPES

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
    },
    "vc_enter": {
        "{user}": "@Usuario",
        "{usertag}": "usuario",
        "{userid}": "123456789012345678",
        "{channel}": "#canal-de-voz",
        "{channelid}": "123456789012345679"
    },
    "vc_leave": {
        "{user}": "@Usuario",
        "{usertag}": "usuario",
        "{userid}": "123456789012345678",
        "{channel}": "#canal-de-voz",
        "{channelid}": "123456789012345679"
    },
    "add_usr_rol": {
        "{user}": "@Usuario",
        "{userid}": "123456789012345678",
        "{usertag}": "usuario",
        "{role}": "@Rol",
        "{roleid}": "123456789012345680"
    },
    "rm_usr_rol": {
        "{user}": "@Usuario",
        "{userid}": "123456789012345678",
        "{usertag}": "usuario",
        "{role}": "@Rol",
        "{roleid}": "123456789012345680"
    },
    "add_ch": {
        "{channelid}": "123456789012345679",
        "{channel}": "#nuevo-canal",
        "{category}": "General",
        "{perms}": "Permisos para `@everyone`:\n- Ver canal ✔️\n- Conectar ❌\n\nPermisos para `@Usuario`:\n- Ver canal ❌\n- Enviar mensajes ✔️"
    },
    "del_ch": {
        "{channelid}": "123456789012345679",
        "{channel}": "#canal-eliminado",
        "{category}": "General"
    },
    "mod_ch": {
        "{channelid}": "123456789012345679",
        "{channel}": "#canal-modificado"
    },
    "add_cat": {
        "{categoryid}": "123456789012345681",
        "{category}": "Nueva Categoría",
        "{perms}": "Permisos para `@everyone`:\n- Ver canales ✔️\n\nPermisos para `@Usuario`:\n- Gestionar canales ✔️"
    },
    "del_cat": {
        "{categoryid}": "123456789012345681",
        "{category}": "Categoría Eliminada"
    },
    "mod_cat": {
        "{categoryid}": "123456789012345681",
        "{category}": "Categoría Modificada"
    },
    "changed_av": {
        "{user}": "@Usuario",
        "{userid}": "123456789012345678",
        "{usertag}": "usuario",
        "{old_avatar_link}": "[antiguo avatar](https://cdn.iconscout.com/icon/free/png-256/free-diablo-2689448-2232249.png)",
        "{new_avatar_link}": "[nuevo avatar](https://archive.org/download/discordprofilepictures/discordblue.png)",
        "{old_name}": "otronombre",
        "{new_name}": "usuario"
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
            
            if log_type == "mod_ch" and message_config.get("changedname", False):
                embed.add_field(
                    name="Actualización del nombre",
                    value="#nombre-antiguo -> #nombre-nuevo",
                    inline=False
                )
                
            if log_type == "mod_ch" and message_config.get("changedperms", False):
                embed.add_field(
                    name="Cambios en permisos",
                    value="Cambios para `@everyone`:\n- Ver canal: ❌ -> ✔️\n\nCambios para `@Usuario`:\n- Enviar mensajes: ✔️ -> ❌",
                    inline=False
                )
                
            if log_type == "mod_cat" and message_config.get("changedname", False):
                embed.add_field(
                    name="Actualización del nombre",
                    value="Nombre Antiguo -> Nombre Nuevo",
                    inline=False
                )
                
            if log_type == "mod_cat" and message_config.get("changedperms", False):
                embed.add_field(
                    name="Cambios en permisos",
                    value="Cambios para `@everyone`:\n- Ver canales: ❌ -> ✔️\n\nCambios para `@Usuario`:\n- Gestionar canales: ✔️ -> ❌",
                    inline=False
                )
            
            embed.timestamp = discord.utils.utcnow()
            
            log_type_name = {
                "ban": "Logs de baneo de usuarios",
                "kick": "Logs de expulsión de usuarios",
                "unban": "Logs de desbaneo de usuarios",
                "enter": "Logs de entrada de usuarios",
                "leave": "Logs de salida de usuarios",
                "del_msg": "Logs de mensajes eliminados",
                "edited_msg": "Logs de mensajes editados",
                "warn": "Logs de advertencias",
                "unwarn": "Logs de eliminación de advertencias",
                "vc_enter": "Logs de entrada a canales de voz",
                "vc_leave": "Logs de salida de canales de voz",
                "add_usr_rol": "Logs de roles añadidos a usuarios",
                "rm_usr_rol": "Logs de roles removidos de usuarios",
                "add_ch": "Logs de canales creados",
                "del_ch": "Logs de canales eliminados",
                "mod_ch": "Logs de canales modificados",
                "add_cat": "Logs de categorías creadas",
                "del_cat": "Logs de categorías eliminadas",
                "mod_cat": "Logs de categorías modificadas",
                "changed_av": "Logs de actualización de avatar o nombre"
            }.get(log_type, "Logs")
            
            content = f"**Configuración de {log_type_name}**\n"
            content += "**Tipo de mensaje:** Embed\n"
            content += f"**Color:** {COLORS.get(color_name, COLORS['default'])[1]}\n"
            
            if message_config.get("thumbnail", {}).get("has", False):
                content += f"**Thumbnail:** Activado\n"
            else:
                content += f"**Thumbnail:** Desactivado\n"
                
            if message_config.get("image", {}).get("has", False):
                content += f"**Imagen:** Activada\n"
            else:
                content += f"**Imagen:** Desactivada\n"
                
            fields_count = len(message_config.get("fields", {}))
            content += f"**Campos:** {fields_count}"
            
            if log_type in ["mod_ch", "mod_cat"]:
                content += "\n\n**Opciones adicionales:**"
                content += f"\n• Registrar cambios de nombre: {'✅' if message_config.get('changedname', False) else '❌'}"
                content += f"\n• Registrar cambios de permisos: {'✅' if message_config.get('changedperms', False) else '❌'}"
            
            return {
                "content": content,
                "embed": embed
            }
        
        else:
            message = message_config.get("message", "")
            if not message:
                return {
                    "content": f"**Configuración de {LOG_TYPES[log_type]['name']}**\n**Tipo de mensaje:** Normal\n**No hay mensaje configurado**"
                }

            message_with_vars = replace_variables(message, replacements)

            display_message = message_with_vars[:100] + ('...' if len(message_with_vars) > 100 else '')
            
            log_type_name = {
                "ban": "Logs de baneo de usuarios",
                "kick": "Logs de expulsión de usuarios",
                "unban": "Logs de desbaneo de usuarios",
                "enter": "Logs de entrada de usuarios",
                "leave": "Logs de salida de usuarios",
                "del_msg": "Logs de mensajes eliminados",
                "edited_msg": "Logs de mensajes editados",
                "warn": "Logs de advertencias",
                "unwarn": "Logs de eliminación de advertencias",
                "vc_enter": "Logs de entrada a canales de voz",
                "vc_leave": "Logs de salida de canales de voz",
                "add_usr_rol": "Logs de roles añadidos a usuarios",
                "rm_usr_rol": "Logs de roles removidos de usuarios",
                "add_ch": "Logs de canales creados",
                "del_ch": "Logs de canales eliminados",
                "mod_ch": "Logs de canales modificados",
                "add_cat": "Logs de categorías creadas",
                "del_cat": "Logs de categorías eliminadas",
                "mod_cat": "Logs de categorías modificadas",
                "changed_av": "Logs de actualización de avatar o nombre"
            }.get(log_type, "Logs")
            
            content = f"**Configuración de {log_type_name}**\n"
            content += "**Tipo de mensaje:** Normal\n"
            content += f"**Mensaje configurado:**\n```\n{display_message}\n```"
            
            if log_type in ["mod_ch", "mod_cat"]:
                content += "\n**Opciones adicionales:**"
                content += f"\n• Registrar cambios de nombre: {'✅' if message_config.get('changedname', False) else '❌'}"
                content += f"\n• Registrar cambios de permisos: {'✅' if message_config.get('changedperms', False) else '❌'}"
            
            return {"content": content}
            
    except Exception as e:
        print(f"Error en create_preview: {e}")
        return {"content": f"Error al generar vista previa: {str(e)}"}