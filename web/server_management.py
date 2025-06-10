from database.get import get_server_data
from database.update import update_multiple_fields
from web.logs_management import LogsManager

class ServerManager:
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.logs_manager = LogsManager(bot_instance)
    
    def get_server_config(self, guild_id):
        try:
            server_data = get_server_data(guild_id)
            if not server_data:
                return None
            
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                return None
            
            config = {
                'guild_info': {
                    'id': str(guild.id),
                    'name': guild.name,
                    'icon': f"https://cdn.discordapp.com/icons/{guild.id}/{guild.icon}.png" if guild.icon else None,
                    'member_count': guild.member_count
                },
                'commands': {
                    'active': server_data.get('act_cmd', []),
                    'inactive': server_data.get('deact_cmd', []),
                    'default': server_data.get('default_cdm', [])
                },
                'permissions': server_data.get('perms', {}),
                'logs': server_data.get('logs', {}),
                'language': server_data.get('language', 'es')
            }
            
            return config
            
        except Exception as e:
            print(f"Error obteniendo configuración del servidor: {e}")
            return None
    
    def get_commands_config(self, guild_id):
        try:
            server_data = get_server_data(guild_id)
            if not server_data:
                return {'error': 'No se encontró configuración del servidor'}
            
            active_commands = server_data.get('act_cmd', [])
            inactive_commands = server_data.get('deact_cmd', [])
            default_commands = server_data.get('default_cdm', [])
            
            all_commands = list(set(active_commands + inactive_commands))
            
            commands_status = {}
            for cmd in all_commands:
                commands_status[cmd] = {
                    'active': cmd in active_commands,
                    'default': cmd in default_commands,
                    'can_modify': cmd not in default_commands
                }
            
            return {
                'commands': commands_status,
                'total_commands': len(all_commands),
                'active_count': len(active_commands),
                'inactive_count': len(inactive_commands)
            }
            
        except Exception as e:
            print(f"Error obteniendo comandos: {e}")
            return {'error': str(e)}
    
    def update_commands_config(self, guild_id, command_updates):
        try:
            server_data = get_server_data(guild_id)
            if not server_data:
                return False
            
            active_commands = server_data.get('act_cmd', []).copy()
            inactive_commands = server_data.get('deact_cmd', []).copy()
            default_commands = server_data.get('default_cdm', [])
            
            for command, should_be_active in command_updates.items():
                if command in default_commands:
                    continue
                
                if should_be_active:
                    if command in inactive_commands:
                        inactive_commands.remove(command)
                    if command not in active_commands:
                        active_commands.append(command)
                else:
                    if command in active_commands:
                        active_commands.remove(command)
                    if command not in inactive_commands:
                        inactive_commands.append(command)
            
            updates = {
                'act_cmd': active_commands,
                'deact_cmd': inactive_commands
            }
            
            return update_multiple_fields(guild_id, updates)
            
        except Exception as e:
            print(f"Error actualizando comandos: {e}")
            return False
    
    def get_server_permissions(self, guild_id):
        try:
            server_data = get_server_data(guild_id)
            if not server_data:
                return {'error': 'No se encontró configuración del servidor'}
            
            permissions = server_data.get('perms', {})
            return {'permissions': permissions}
            
        except Exception as e:
            print(f"Error obteniendo permisos: {e}")
            return {'error': str(e)}
    
    def get_server_logs(self, guild_id):
        try:
            return self.logs_manager.get_all_logs(guild_id)
        except Exception as e:
            print(f"Error obteniendo logs: {e}")
            return {'error': str(e)}