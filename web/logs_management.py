from database.get import get_specific_field, get_server_data
from database.update import update_server_data
import copy

LOG_TYPES = {
    "ban": {
        "name": "Logs de baneo de usuarios",
        "description": "Registra cuando un usuario es baneado del servidor",
        "params": ["{userid}", "{usertag}", "{mod}", "{modid}", "{modtag}", "{reason}"],
        "footer_params": ["{userid}", "{usertag}", "{modid}", "{modtag}"]
    },
    "kick": {
        "name": "Logs de expulsión de usuarios", 
        "description": "Registra cuando un usuario es expulsado del servidor",
        "params": ["{userid}", "{usertag}", "{mod}", "{modid}", "{modtag}", "{reason}"],
        "footer_params": ["{userid}", "{usertag}", "{modid}", "{modtag}"]
    },
    "unban": {
        "name": "Logs de desbaneo de usuarios",
        "description": "Registra cuando un usuario es desbaneado",
        "params": ["{userid}", "{usertag}", "{modtag}", "{modid}", "{mod}"],
        "footer_params": ["{userid}", "{usertag}", "{modtag}", "{modid}"]
    },
    "enter": {
        "name": "Logs de entrada de usuarios",
        "description": "Registra cuando un usuario se une al servidor",
        "params": ["{userid}", "{usertag}", "{user}", "{accage}"],
        "footer_params": ["{userid}", "{usertag}", "{user}"]
    },
    "leave": {
        "name": "Logs de salida de usuarios",
        "description": "Registra cuando un usuario abandona el servidor",
        "params": ["{userid}", "{usertag}"],
        "footer_params": ["{userid}", "{usertag}"]
    },
    "del_msg": {
        "name": "Logs de mensajes eliminados",
        "description": "Registra cuando se elimina un mensaje",
        "params": ["{del_msg}", "{usertag}", "{userid}", "{user}", "{channel}", "{channelid}"],
        "footer_params": ["{usertag}", "{userid}", "{channelid}"]
    },
    "edited_msg": {
        "name": "Logs de mensajes editados",
        "description": "Registra cuando se edita un mensaje",
        "params": ["{user}", "{userid}", "{usertag}", "{channel}", "{channelid}", "{old_msg}", "{new_msg}"],
        "footer_params": ["{userid}", "{usertag}", "{channelid}"]
    },
    "warn": {
        "name": "Logs de advertencias",
        "description": "Registra cuando se da una advertencia a un usuario",
        "params": ["{user}", "{userid}", "{usertag}", "{reason}", "{mod}", "{modtag}", "{modid}", "{warnid}"],
        "footer_params": ["{userid}", "{usertag}", "{modid}", "{modtag}"]
    },
    "unwarn": {
        "name": "Logs de eliminación de advertencias",
        "description": "Registra cuando se elimina una advertencia",
        "params": ["{user}", "{userid}", "{usertag}", "{reason}", "{mod}", "{modtag}", "{modid}", "{warnid}"],
        "footer_params": ["{userid}", "{usertag}", "{modid}", "{modtag}"]
    },
    "vc_enter": {
        "name": "Logs de entrada a canales de voz",
        "description": "Registra cuando un usuario se conecta a un canal de voz",
        "params": ["{user}", "{usertag}", "{userid}", "{channel}", "{channelid}"],
        "footer_params": ["{usertag}", "{userid}", "{channelid}"]
    },
    "vc_leave": {
        "name": "Logs de salida de canales de voz",
        "description": "Registra cuando un usuario se desconecta de un canal de voz",
        "params": ["{user}", "{usertag}", "{userid}", "{channel}", "{channelid}"],
        "footer_params": ["{usertag}", "{userid}", "{channelid}"]
    },
    "add_usr_rol": {
        "name": "Logs de roles añadidos a usuarios",
        "description": "Registra cuando se añade un rol a un usuario",
        "params": ["{user}", "{usertag}", "{userid}", "{role}", "{roleid}"],
        "footer_params": ["{usertag}", "{userid}", "{roleid}"]
    },
    "rm_usr_rol": {
        "name": "Logs de roles removidos de usuarios",
        "description": "Registra cuando se remueve un rol de un usuario",
        "params": ["{user}", "{usertag}", "{userid}", "{role}", "{roleid}"],
        "footer_params": ["{usertag}", "{userid}", "{roleid}"]
    },
    "add_ch": {
        "name": "Logs de canales creados",
        "description": "Registra cuando se crea un canal",
        "params": ["{channel}", "{channelid}", "{category}", "{perms}"],
        "footer_params": ["{channelid}"]
    },
    "del_ch": {
        "name": "Logs de canales eliminados",
        "description": "Registra cuando se elimina un canal",
        "params": ["{channel}", "{channelid}", "{category}"],
        "footer_params": ["{channelid}"]
    },
    "mod_ch": {
        "name": "Logs de canales modificados",
        "description": "Registra cuando se modifica un canal",
        "params": ["{channel}", "{channelid}"],
        "footer_params": ["{channelid}"],
        "config_options": ["changedname", "changedperms"]
    },
    "add_cat": {
        "name": "Logs de categorías creadas",
        "description": "Registra cuando se crea una categoría",
        "params": ["{category}", "{categoryid}", "{perms}"],
        "footer_params": ["{categoryid}"]
    },
    "del_cat": {
        "name": "Logs de categorías eliminadas",
        "description": "Registra cuando se elimina una categoría",
        "params": ["{category}", "{categoryid}"],
        "footer_params": ["{categoryid}"]
    },
    "mod_cat": {
        "name": "Logs de categorías modificadas",
        "description": "Registra cuando se modifica una categoría",
        "params": ["{category}", "{categoryid}"],
        "footer_params": ["{categoryid}"],
        "config_options": ["changedname", "changedperms"]
    },
    "changed_av": {
        "name": "Logs de actualización de avatar o nombre",
        "description": "Registra cuando un usuario cambia su avatar o nombre",
        "params": ["{user}", "{usertag}", "{userid}", "{old_avatar_link}", "{new_avatar_link}", "{old_name}", "{new_name}"],
        "footer_params": ["{usertag}", "{userid}"]
    }
}

COLORS = {
    "default": {"hex": "#3498db", "name": "Azul", "emoji": "🔵"},
    "red": {"hex": "#e74c3c", "name": "Rojo", "emoji": "🔴"},
    "green": {"hex": "#2ecc71", "name": "Verde", "emoji": "🟢"},
    "yellow": {"hex": "#f1c40f", "name": "Amarillo", "emoji": "🟡"},
    "orange": {"hex": "#e67e22", "name": "Naranja", "emoji": "🟠"},
    "purple": {"hex": "#9b59b6", "name": "Morado", "emoji": "🟣"},
    "pink": {"hex": "#ff6b81", "name": "Rosa", "emoji": "🌸"},
    "gray": {"hex": "#95a5a6", "name": "Gris", "emoji": "⚪"},
    "black": {"hex": "#34495e", "name": "Negro", "emoji": "⚫"},
    "white": {"hex": "#ecf0f1", "name": "Blanco", "emoji": "⬜"}
}

class LogsManager:
    def __init__(self, bot_instance):
        self.bot = bot_instance
    
    def get_all_logs(self, guild_id):
        try:
            audit_logs = get_specific_field(guild_id, "audit_logs")
            if not audit_logs:
                return {}
            
            logs_status = {}
            for log_type in LOG_TYPES:
                if log_type in audit_logs:
                    log_config = audit_logs[log_type]
                    channel_name = 'No configurado'
                    if log_config.get('log_channel'):
                        guild = self.bot.get_guild(int(guild_id))
                        if guild:
                            channel = guild.get_channel(int(log_config['log_channel']))
                            channel_name = channel.name if channel else 'Canal eliminado'
                    
                    logs_status[log_type] = {
                        'name': LOG_TYPES[log_type]['name'],
                        'description': LOG_TYPES[log_type].get('description', ''),
                        'activated': log_config.get('activated', False),
                        'log_channel': log_config.get('log_channel', 0),
                        'channel_name': channel_name,
                        'has_message': bool(log_config.get('message', {})),
                        'message_type': 'Embed' if log_config.get('message', {}).get('embed', False) else 'Texto',
                        'config_options': LOG_TYPES[log_type].get('config_options', [])
                    }
                else:
                    logs_status[log_type] = {
                        'name': LOG_TYPES[log_type]['name'],
                        'description': LOG_TYPES[log_type].get('description', ''),
                        'activated': False,
                        'log_channel': 0,
                        'channel_name': 'No configurado',
                        'has_message': False,
                        'message_type': 'No configurado',
                        'config_options': LOG_TYPES[log_type].get('config_options', [])
                    }
            
            return logs_status
        except Exception as e:
            print(f"Error obteniendo logs: {e}")
            return {}
    
    def get_log_config(self, guild_id, log_type):
        try:
            if log_type not in LOG_TYPES:
                return None
            
            audit_logs = get_specific_field(guild_id, "audit_logs")
            if not audit_logs or log_type not in audit_logs:
                return self._create_default_log_config(log_type)
            
            log_config = audit_logs[log_type]
            guild = self.bot.get_guild(int(guild_id))
            
            if guild and log_config.get('log_channel'):
                channel = guild.get_channel(int(log_config['log_channel']))
                log_config['channel_name'] = channel.name if channel else 'Canal eliminado'
            else:
                log_config['channel_name'] = 'No configurado'
            
            if not log_config.get('message'):
                log_config['message'] = self._create_default_message()
            
            log_config['log_info'] = LOG_TYPES[log_type]
            return log_config
        except Exception as e:
            print(f"Error obteniendo configuración de log: {e}")
            return None
    
    def _create_default_log_config(self, log_type):
        return {
            'activated': False,
            'log_channel': 0,
            'channel_name': 'No configurado',
            'message': self._create_default_message(),
            'log_info': LOG_TYPES[log_type]
        }
    
    def _create_default_message(self):
        return {
            "embed": True,
            "title": "",
            "description": "",
            "footer": "",
            "color": "default",
            "image": {"has": False, "param": ""},
            "thumbnail": {"has": False, "param": ""},
            "fields": {},
            "message": ""
        }
    
    def save_log_config(self, guild_id, log_type, config):
        try:
            if log_type not in LOG_TYPES:
                return False
            
            if not config.get('message'):
                config['message'] = self._create_default_message()
            
            if not config.get('log_channel'):
                return False
            
            result = update_server_data(guild_id, f"audit_logs/{log_type}", config)
            return result
        except Exception as e:
            print(f"Error guardando configuración de log: {e}")
            return False
    
    def get_guild_channels(self, guild_id):
        try:
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                return []
            
            text_channels = []
            for channel in guild.text_channels:
                text_channels.append({
                    'id': str(channel.id),
                    'name': channel.name
                })
            
            return text_channels
        except Exception as e:
            print(f"Error obteniendo canales: {e}")
            return []
    
    def get_colors(self):
        return COLORS
    
    def get_log_types(self):
        return LOG_TYPES
    
    def generate_preview_data(self, log_type, message_config, guild_id):
        try:
            if log_type not in LOG_TYPES:
                return None
            
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                return None
            
            preview = self._generate_message_preview(message_config, log_type, guild)
            return preview
        except Exception as e:
            print(f"Error generando preview: {e}")
            return None
    
    def _generate_message_preview(self, message_config, log_type, guild):
        try:
            preview = {
                'content': '',
                'embed': None
            }
            
            if message_config.get('plain_message') or message_config.get('message'):
                content = message_config.get('plain_message', '') or message_config.get('message', '')
                preview['content'] = self._apply_sample_params(content, log_type)
            
            if message_config.get('embed'):
                color_name = message_config.get('color', 'default')
                color_data = COLORS.get(color_name, COLORS['default'])
                
                embed = {
                    'title': self._apply_sample_params(message_config.get('title', ''), log_type),
                    'description': self._apply_sample_params(message_config.get('description', ''), log_type),
                    'color': color_data['hex'],
                    'color_name': color_data['name'],
                    'footer': self._apply_sample_params(message_config.get('footer', ''), log_type),
                    'fields': []
                }
                
                if message_config.get('image', {}).get('has') and message_config.get('image', {}).get('param'):
                    embed['image'] = message_config['image']['param']
                
                if message_config.get('thumbnail', {}).get('has') and message_config.get('thumbnail', {}).get('param'):
                    embed['thumbnail'] = message_config['thumbnail']['param']
                
                fields = message_config.get('fields', {})
                if fields:
                    sorted_fields = sorted(fields.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 999)
                    for field_id, field_data in sorted_fields:
                        embed['fields'].append({
                            'name': self._apply_sample_params(field_data.get('name', ''), log_type),
                            'value': self._apply_sample_params(field_data.get('value', ''), log_type),
                            'inline': field_data.get('inline', False)
                        })
                
                preview['embed'] = embed
            
            preview['log_info'] = LOG_TYPES.get(log_type, {})
            preview['params'] = LOG_TYPES.get(log_type, {}).get('params', [])
            
            return preview
        except Exception as e:
            print(f"Error generando preview de mensaje: {e}")
            return {'content': 'Error en preview', 'embed': None}
    
    def _apply_sample_params(self, text, log_type):
        if not text:
            return text
        
        sample_values = {
            "{userid}": "123456789012345678",
            "{usertag}": "Usuario#1234",
            "{user}": "@Usuario",
            "{mod}": "@Moderador",
            "{modid}": "987654321098765432",
            "{modtag}": "Moderador#5678",
            "{reason}": "Violación de las reglas del servidor",
            "{channel}": "#general",
            "{channelid}": "111222333444555666",
            "{category}": "Categoría General",
            "{categoryid}": "777888999000111222",
            "{role}": "@Miembro",
            "{roleid}": "333444555666777888",
            "{accage}": "30 días",
            "{del_msg}": "Este es un mensaje que fue eliminado",
            "{old_msg}": "Mensaje original",
            "{new_msg}": "Mensaje editado",
            "{warnid}": "WARN001",
            "{old_avatar_link}": "[avatar anterior](https://example.com/old.png)",
            "{new_avatar_link}": "[avatar nuevo](https://example.com/new.png)",
            "{old_name}": "NombreAnterior",
            "{new_name}": "NombreNuevo",
            "{perms}": "Ver canal, Enviar mensajes"
        }
        
        for param, value in sample_values.items():
            text = text.replace(param, value)
        
        return text
    
    def validate_log_config(self, config):
        if not config.get('log_channel'):
            return False, "Debe seleccionar un canal para los logs"
        
        message_config = config.get('message', {})
        if message_config.get('embed'):
            if not message_config.get('description', '').strip():
                return False, "El embed debe tener una descripción"
        else:
            if not message_config.get('message', '').strip():
                return False, "Debe configurar un mensaje de texto"
        
        return True, "Configuración válida"