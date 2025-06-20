from commands.tickets.utils.database import get_tickets_data, get_ticket_data, save_ticket_config, delete_ticket_config
from commands.tickets.constants import DEFAULT_TICKET_CONFIG, COLORS, PERMISSIONS_DESCRIPTIONS
from database.get import get_server_data
import copy
import asyncio

class TicketsManager:
    def __init__(self, bot_instance):
        self.bot = bot_instance
    
    def get_all_tickets(self, guild_id):
        try:
            tickets_data = get_tickets_data(guild_id)
            if not tickets_data:
                return []
            
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                return []
            
            tickets_list = []
            for channel_id, ticket_config in tickets_data.items():
                channel = guild.get_channel(int(channel_id))
                if channel and isinstance(ticket_config, dict) and not ticket_config.get('__deleted', False):
                    log_channel = None
                    log_channel_id = ticket_config.get('log_channel')
                    if log_channel_id:
                        log_channel = guild.get_channel(int(log_channel_id))
                    
                    tickets_list.append({
                        'channel_id': channel_id,
                        'channel_name': channel.name,
                        'log_channel_name': log_channel.name if log_channel else 'No configurado',
                        'buttons_count': len(ticket_config.get('open_message', {}).get('buttons', [])),
                        'has_permissions': bool(ticket_config.get('permissions', {}).get('manage', {}).get('roles') or 
                                              ticket_config.get('permissions', {}).get('manage', {}).get('users'))
                    })
            
            return tickets_list
        except Exception as e:
            print(f"Error obteniendo tickets: {e}")
            return []
    
    def get_ticket_config(self, guild_id, channel_id):
        try:
            ticket_config = get_ticket_data(guild_id, channel_id)
            if not ticket_config:
                return None
            
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                return None
            
            channel = guild.get_channel(int(channel_id))
            log_channel = None
            if ticket_config.get('log_channel'):
                log_channel = guild.get_channel(int(ticket_config['log_channel']))
            
            processed_config = copy.deepcopy(ticket_config)
            
            if 'permissions' in processed_config:
                for perm_type in ['manage', 'view']:
                    if perm_type in processed_config['permissions']:
                        roles_info = []
                        for role_id in processed_config['permissions'][perm_type].get('roles', []):
                            role = guild.get_role(int(role_id))
                            if role:
                                roles_info.append({'id': str(role.id), 'name': role.name})
                        
                        users_info = []
                        for user_id in processed_config['permissions'][perm_type].get('users', []):
                            try:
                                member = guild.get_member(int(user_id))
                                if member:
                                    users_info.append({'id': str(member.id), 'name': str(member)})
                            except:
                                pass
                        
                        processed_config['permissions'][perm_type]['roles_info'] = roles_info
                        processed_config['permissions'][perm_type]['users_info'] = users_info
            
            return {
                'config': processed_config,
                'channel_name': channel.name if channel else 'Canal eliminado',
                'log_channel_name': log_channel.name if log_channel else 'No configurado'
            }
        except Exception as e:
            print(f"Error obteniendo configuración de ticket: {e}")
            return None
    
    def create_default_ticket(self):
        return copy.deepcopy(DEFAULT_TICKET_CONFIG)
    
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
    
    def get_guild_roles(self, guild_id):
        try:
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                return []
            
            roles = []
            for role in guild.roles:
                if role.name != '@everyone':
                    roles.append({
                        'id': str(role.id),
                        'name': role.name,
                        'color': str(role.color) if str(role.color) != '#000000' else '#99aab5'
                    })
            
            return sorted(roles, key=lambda x: x['name'].lower())
        except Exception as e:
            print(f"Error obteniendo roles: {e}")
            return []
    
    def save_ticket_config(self, guild_id, channel_id, config):
        try:
            print(f"[SAVE] Iniciando guardado de ticket para guild {guild_id}, canal {channel_id}")
            
            if not config.get('permissions'):
                config['permissions'] = {
                    'manage': {'roles': [], 'users': []},
                    'view': {'roles': [], 'users': []}
                }
            
            if not config.get('open_message'):
                config['open_message'] = {
                    'embed': True,
                    'title': 'Sistema de Tickets',
                    'description': 'Haz clic en el botón correspondiente para abrir un ticket de soporte.',
                    'footer': '',
                    'color': 'blue',
                    'fields': [],
                    'image': {'url': '', 'enabled': False},
                    'thumbnail': {'url': '', 'enabled': False},
                    'buttons': [{
                        'id': 'default',
                        'label': 'Abrir Ticket',
                        'emoji': '🎫',
                        'style': 3,
                        'name_format': 'ticket-{id}',
                        'description': 'Abrir un ticket de soporte general'
                    }],
                    'plain_message': ''
                }
            
            if not config.get('opened_messages'):
                config['opened_messages'] = {
                    'default': {
                        'embed': True,
                        'title': 'Ticket Abierto',
                        'description': 'Gracias por abrir un ticket. Un miembro del equipo te atenderá lo antes posible.',
                        'footer': '',
                        'color': 'green',
                        'fields': [],
                        'image': {'url': '', 'enabled': False},
                        'thumbnail': {'url': '', 'enabled': False},
                        'plain_message': ''
                    }
                }
            
            if not config.get('auto_increment'):
                config['auto_increment'] = {}
                for button in config.get('open_message', {}).get('buttons', []):
                    config['auto_increment'][button.get('id', 'default')] = 1
            
            async def async_save():
                try:
                    print(f"[SAVE] Llamando a save_ticket_config async")
                    result = await save_ticket_config(guild_id, channel_id, config)
                    print(f"[SAVE] Resultado de save_ticket_config: {result}")
                    
                    if result and hasattr(self.bot, 'ticket_listener') and self.bot.ticket_listener:
                        try:
                            print(f"[SAVE] Ejecutando database listener")
                            await self.bot.ticket_listener.process_ticket_change(
                                guild_id, 
                                str(channel_id), 
                                config
                            )
                            print(f"[SAVE] Database listener ejecutado correctamente para canal {channel_id}")
                        except Exception as e:
                            print(f"[SAVE] Error al ejecutar database listener: {e}")
                            import traceback
                            traceback.print_exc()
                    
                    return result
                except Exception as e:
                    print(f"[SAVE] Error en async_save: {e}")
                    import traceback
                    traceback.print_exc()
                    return False
            
            loop = self.bot.loop if hasattr(self.bot, 'loop') and self.bot.loop else asyncio.get_event_loop()
            
            if loop.is_running():
                future = asyncio.run_coroutine_threadsafe(async_save(), loop)
                result = future.result(timeout=30)
            else:
                result = loop.run_until_complete(async_save())
            
            print(f"[SAVE] Resultado final: {result}")
            return result
            
        except Exception as e:
            print(f"[SAVE] Error guardando configuración: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def delete_ticket(self, guild_id, channel_id):
        try:
            print(f"[DELETE] Iniciando eliminación de ticket para guild {guild_id}, canal {channel_id}")
            
            async def async_delete():
                try:
                    guild = self.bot.get_guild(int(guild_id))
                    if guild:
                        channel = guild.get_channel(int(channel_id))
                        if channel:
                            async for message in channel.history(limit=100):
                                if message.author.id == self.bot.user.id and message.components:
                                    for row in message.components:
                                        for component in row.children:
                                            if hasattr(component, 'custom_id') and component.custom_id and component.custom_id.startswith(f"ticket:open:{channel_id}"):
                                                try:
                                                    await message.delete()
                                                    print(f"[DELETE] Mensaje de ticket eliminado del canal {channel_id}")
                                                except Exception as e:
                                                    print(f"[DELETE] Error eliminando mensaje: {e}")
                                                break
                    
                    result = await delete_ticket_config(guild_id, channel_id)
                    print(f"[DELETE] Resultado de delete_ticket_config: {result}")
                    
                    if result and hasattr(self.bot, 'ticket_listener') and self.bot.ticket_listener:
                        try:
                            print(f"[DELETE] Ejecutando database listener para eliminación")
                            await self.bot.ticket_listener.process_ticket_deletion(
                                guild_id, 
                                str(channel_id)
                            )
                            print(f"[DELETE] Database listener ejecutado correctamente para eliminación en canal {channel_id}")
                        except Exception as e:
                            print(f"[DELETE] Error al ejecutar database listener para eliminación: {e}")
                            import traceback
                            traceback.print_exc()
                    
                    return result
                except Exception as e:
                    print(f"[DELETE] Error en async_delete: {e}")
                    import traceback
                    traceback.print_exc()
                    return False
            
            loop = self.bot.loop if hasattr(self.bot, 'loop') and self.bot.loop else asyncio.get_event_loop()
            
            if loop.is_running():
                future = asyncio.run_coroutine_threadsafe(async_delete(), loop)
                result = future.result(timeout=30)
            else:
                result = loop.run_until_complete(async_delete())
            
            print(f"[DELETE] Resultado final: {result}")
            return result
            
        except Exception as e:
            print(f"[DELETE] Error eliminando ticket: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_colors(self):
        return COLORS
    
    def get_permission_descriptions(self):
        return PERMISSIONS_DESCRIPTIONS
    
    def generate_preview_data(self, config, guild_id):
        try:
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                return None
            
            preview = {
                'open_message': self._generate_message_preview(config.get('open_message', {}), 'open'),
                'opened_messages': {}
            }
            
            opened_messages = config.get('opened_messages', {})
            for button_id, message_config in opened_messages.items():
                preview['opened_messages'][button_id] = self._generate_message_preview(message_config, 'opened')
            
            return preview
        except Exception as e:
            print(f"Error generando preview: {e}")
            return None
    
    def _generate_message_preview(self, message_config, message_type):
        try:
            preview = {
                'content': '',
                'embed': None
            }
            
            if message_config.get('plain_message'):
                preview['content'] = message_config['plain_message']
            
            if message_config.get('embed'):
                color_name = message_config.get('color', 'blue')
                color_value = COLORS.get(color_name, COLORS['blue'])[0]
                
                embed = {
                    'title': message_config.get('title', ''),
                    'description': message_config.get('description', ''),
                    'color': color_name,
                    'footer': message_config.get('footer', ''),
                    'fields': message_config.get('fields', []),
                    'image': message_config.get('image', {}).get('url', '') if message_config.get('image', {}).get('enabled') else None,
                    'thumbnail': message_config.get('thumbnail', {}).get('url', '') if message_config.get('thumbnail', {}).get('enabled') else None
                }
                
                preview['embed'] = embed
            
            if message_type == 'open':
                buttons = message_config.get('buttons', [])
                if buttons:
                    preview['buttons'] = []
                    for button in buttons:
                        preview['buttons'].append({
                            'label': button.get('label', 'Botón'),
                            'emoji': button.get('emoji', ''),
                            'style': button.get('style', 3),
                            'id': button.get('id', 'default')
                        })
                
            elif message_type == 'opened':
                preview['control_buttons'] = [
                    {'label': 'Archivar Ticket', 'emoji': '🔒'},
                    {'label': 'Añadir Usuario', 'emoji': '➕'},
                    {'label': 'Eliminar Usuario', 'emoji': '➖'}
                ]
            
            return preview
        except Exception as e:
            print(f"Error generando preview de mensaje: {e}")
            return {'content': 'Error en preview', 'embed': None}
    
    def get_ticket_permissions(self, guild_id, channel_id):
        try:
            ticket_config = get_ticket_data(guild_id, channel_id)
            if not ticket_config:
                return None
            
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                return None
            
            permissions = ticket_config.get('permissions', {
                'manage': {'roles': [], 'users': []},
                'view': {'roles': [], 'users': []}
            })
            
            processed_permissions = {}
            for perm_type in ['manage', 'view']:
                processed_permissions[perm_type] = {
                    'roles': [],
                    'users': []
                }
                
                for role_id in permissions.get(perm_type, {}).get('roles', []):
                    role = guild.get_role(int(role_id))
                    if role:
                        processed_permissions[perm_type]['roles'].append({
                            'id': str(role.id),
                            'name': role.name,
                            'color': str(role.color) if str(role.color) != '#000000' else '#99aab5'
                        })
                
                for user_id in permissions.get(perm_type, {}).get('users', []):
                    try:
                        member = guild.get_member(int(user_id))
                        if member:
                            processed_permissions[perm_type]['users'].append({
                                'id': str(member.id),
                                'name': str(member),
                                'avatar': member.avatar.url if member.avatar else member.default_avatar.url
                            })
                    except:
                        pass
            
            return processed_permissions
        except Exception as e:
            print(f"Error obteniendo permisos de ticket: {e}")
            return None

    def save_ticket_permissions(self, guild_id, channel_id, permissions_data):
        try:
            ticket_config = get_ticket_data(guild_id, channel_id)
            if not ticket_config:
                return False
            
            for perm_type in ['manage', 'view']:
                roles = []
                users = []
                
                for role_id in permissions_data.get(perm_type, {}).get('roles', []):
                    roles.append(str(role_id))
                
                for user_id in permissions_data.get(perm_type, {}).get('users', []):
                    users.append(str(user_id))
                
                ticket_config['permissions'][perm_type] = {
                    'roles': roles,
                    'users': users
                }
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                success = loop.run_until_complete(save_ticket_config(guild_id, channel_id, ticket_config))
                return success
            finally:
                loop.close()
                
        except Exception as e:
            print(f"Error guardando permisos de ticket: {e}")
            return False

    def add_ticket_permission(self, guild_id, channel_id, perm_type, item_type, item_id):
        try:
            ticket_config = get_ticket_data(guild_id, channel_id)
            if not ticket_config:
                return False, "Ticket no encontrado"
            
            if 'permissions' not in ticket_config:
                ticket_config['permissions'] = {
                    'manage': {'roles': [], 'users': []},
                    'view': {'roles': [], 'users': []}
                }
            
            if perm_type not in ticket_config['permissions']:
                ticket_config['permissions'][perm_type] = {'roles': [], 'users': []}
            
            if item_type not in ticket_config['permissions'][perm_type]:
                ticket_config['permissions'][perm_type][item_type] = []
            
            item_id_str = str(item_id)
            if item_id_str not in [str(x) for x in ticket_config['permissions'][perm_type][item_type]]:
                ticket_config['permissions'][perm_type][item_type].append(item_id_str)
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    success = loop.run_until_complete(save_ticket_config(guild_id, channel_id, ticket_config))
                    if success:
                        return True, "Elemento añadido correctamente"
                    else:
                        return False, "Error al guardar"
                finally:
                    loop.close()
            else:
                return False, "El elemento ya existe"
                
        except Exception as e:
            print(f"Error añadiendo permiso: {e}")
            return False, "Error interno"

    def remove_ticket_permission(self, guild_id, channel_id, perm_type, item_type, item_id):
        try:
            ticket_config = get_ticket_data(guild_id, channel_id)
            if not ticket_config:
                return False, "Ticket no encontrado"
            
            if ('permissions' not in ticket_config or 
                perm_type not in ticket_config['permissions'] or
                item_type not in ticket_config['permissions'][perm_type]):
                return False, "Permiso no encontrado"
            
            item_id_str = str(item_id)
            items_to_remove = [x for x in ticket_config['permissions'][perm_type][item_type] if str(x) == item_id_str]
            if items_to_remove:
                for item in items_to_remove:
                    ticket_config['permissions'][perm_type][item_type].remove(item)
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    success = loop.run_until_complete(save_ticket_config(guild_id, channel_id, ticket_config))
                    if success:
                        return True, "Elemento eliminado correctamente"
                    else:
                        return False, "Error al guardar"
                finally:
                    loop.close()
            else:
                return False, "El elemento no existe"
                
        except Exception as e:
            print(f"Error eliminando permiso: {e}")
            return False, "Error interno"