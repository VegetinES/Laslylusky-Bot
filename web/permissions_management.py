from database.get import get_server_data
from database.update import update_server_data
import copy

PERMISSION_CATEGORIES = {
    "admin": {
        "name": "Administradores del Bot",
        "description": "Control total sobre la configuración del bot",
        "permissions": {
            "admin-roles": "Roles con permisos de administrador",
            "admin-users": "Usuarios con permisos de administrador"
        }
    },
    "mg-srv": {
        "name": "Gestión del Servidor", 
        "description": "Permisos para gestionar configuraciones del servidor",
        "permissions": {
            "mg-srv-roles": "Roles con permisos de gestión",
            "mg-srv-users": "Usuarios con permisos de gestión"
        }
    },
    "custom": {
        "name": "Permisos Personalizados",
        "description": "Otros permisos específicos configurados",
        "permissions": {}
    }
}

class PermissionsManager:
    def __init__(self, bot_instance):
        self.bot = bot_instance
    
    def get_all_permissions(self, guild_id):
        try:
            server_data = get_server_data(guild_id)
            if not server_data:
                return {}
            
            perms = server_data.get('perms', {})
            organized_perms = copy.deepcopy(PERMISSION_CATEGORIES)
            
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                return organized_perms
            
            for perm_key, perm_value in perms.items():
                if perm_key.endswith('-roles') or perm_key.endswith('-users'):
                    base_perm = perm_key.rsplit('-', 1)[0]
                    perm_type = perm_key.rsplit('-', 1)[1]
                    
                    category = self._get_permission_category(base_perm)
                    
                    if category == "custom":
                        roles_key = f"{base_perm}-roles"
                        users_key = f"{base_perm}-users"
                        if roles_key not in organized_perms[category]["permissions"]:
                            organized_perms[category]["permissions"][roles_key] = f"Roles con permiso {base_perm}"
                        if users_key not in organized_perms[category]["permissions"]:
                            organized_perms[category]["permissions"][users_key] = f"Usuarios con permiso {base_perm}"
                    
                    processed_value = []
                    if perm_value and perm_value != 0:
                        if isinstance(perm_value, list):
                            for item_id in perm_value:
                                if perm_type == 'roles':
                                    role = guild.get_role(int(item_id))
                                    if role:
                                        processed_value.append({
                                            'id': item_id,
                                            'name': role.name,
                                            'color': str(role.color) if str(role.color) != '#000000' else '#99aab5'
                                        })
                                else:
                                    member = guild.get_member(int(item_id))
                                    if member:
                                        processed_value.append({
                                            'id': item_id,
                                            'name': str(member),
                                            'avatar': member.avatar.url if member.avatar else member.default_avatar.url
                                        })
                    
                    organized_perms[category][perm_key] = {
                        "type": perm_type,
                        "base_permission": base_perm,
                        "items": processed_value,
                        "count": len(processed_value)
                    }
            
            return organized_perms
            
        except Exception as e:
            print(f"Error obteniendo permisos: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def _get_permission_category(self, base_perm):
        for category, data in PERMISSION_CATEGORIES.items():
            if category == "custom":
                continue
            for perm_key in data["permissions"].keys():
                if perm_key.startswith(base_perm):
                    return category
        return "custom"
    
    def get_permission_details(self, guild_id, permission_key):
        try:
            server_data = get_server_data(guild_id)
            if not server_data:
                return None
            
            perms = server_data.get('perms', {})
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                return None
            
            if permission_key not in perms:
                base_perm = permission_key.rsplit('-', 1)[0]
                return {
                    "permission": permission_key,
                    "base_permission": base_perm,
                    "type": permission_key.rsplit('-', 1)[1],
                    "items": [],
                    "available_roles": self._get_available_roles(guild),
                    "description": self._get_permission_description(permission_key)
                }
            
            perm_value = perms[permission_key]
            perm_type = permission_key.rsplit('-', 1)[1]
            base_perm = permission_key.rsplit('-', 1)[0]
            
            items = []
            if perm_value and perm_value != 0:
                if isinstance(perm_value, list):
                    for item_id in perm_value:
                        if perm_type == 'roles':
                            role = guild.get_role(int(item_id))
                            if role:
                                items.append({
                                    'id': item_id,
                                    'name': role.name,
                                    'color': str(role.color) if str(role.color) != '#000000' else '#99aab5'
                                })
                        else:
                            member = guild.get_member(int(item_id))
                            if member:
                                items.append({
                                    'id': item_id,
                                    'name': str(member),
                                    'avatar': member.avatar.url if member.avatar else member.default_avatar.url
                                })
            
            return {
                "permission": permission_key,
                "base_permission": base_perm,
                "type": perm_type,
                "items": items,
                "available_roles": self._get_available_roles(guild) if perm_type == 'roles' else [],
                "description": self._get_permission_description(permission_key)
            }
            
        except Exception as e:
            print(f"Error obteniendo detalles del permiso: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _get_available_roles(self, guild):
        roles = []
        for role in guild.roles:
            if role.name != '@everyone':
                roles.append({
                    'id': str(role.id),
                    'name': role.name,
                    'color': str(role.color) if str(role.color) != '#000000' else '#99aab5'
                })
        return sorted(roles, key=lambda x: x['name'].lower())
    
    def _get_permission_description(self, permission_key):
        for category_data in PERMISSION_CATEGORIES.values():
            if permission_key in category_data["permissions"]:
                return category_data["permissions"][permission_key]
        
        base_perm = permission_key.rsplit('-', 1)[0]
        perm_type = permission_key.rsplit('-', 1)[1]
        type_text = "Roles" if perm_type == "roles" else "Usuarios"
        return f"{type_text} con permiso {base_perm}"
    
    def add_permission_item(self, guild_id, permission_key, item_id, item_type):
        try:
            server_data = get_server_data(guild_id)
            if not server_data:
                return False, "No se encontraron datos del servidor"
            
            perms = server_data.get('perms', {})
            current_items = perms.get(permission_key, [])
            
            if current_items == 0:
                current_items = []
            
            item_id = int(item_id)
            
            if item_id not in current_items:
                current_items.append(item_id)
                
                success = update_server_data(guild_id, f'perms/{permission_key}', current_items)
                if success:
                    return True, "Elemento añadido correctamente"
                else:
                    return False, "Error al actualizar la base de datos"
            else:
                return False, "El elemento ya existe en este permiso"
                
        except Exception as e:
            print(f"Error añadiendo elemento al permiso: {e}")
            import traceback
            traceback.print_exc()
            return False, "Error interno del servidor"
    
    def remove_permission_item(self, guild_id, permission_key, item_id):
        try:
            server_data = get_server_data(guild_id)
            if not server_data:
                return False, "No se encontraron datos del servidor"
            
            perms = server_data.get('perms', {})
            current_items = perms.get(permission_key, [])
            
            if current_items == 0:
                current_items = []
            
            item_id = int(item_id)
            
            if item_id in current_items:
                current_items.remove(item_id)
                
                final_value = current_items if current_items else 0
                success = update_server_data(guild_id, f'perms/{permission_key}', final_value)
                if success:
                    return True, "Elemento eliminado correctamente"
                else:
                    return False, "Error al actualizar la base de datos"
            else:
                return False, "El elemento no existe en este permiso"
                
        except Exception as e:
            print(f"Error eliminando elemento del permiso: {e}")
            import traceback
            traceback.print_exc()
            return False, "Error interno del servidor"
    
    def create_custom_permission(self, guild_id, permission_name):
        try:
            server_data = get_server_data(guild_id)
            if not server_data:
                return False, "No se encontraron datos del servidor"
            
            perms = server_data.get('perms', {})
            
            roles_key = f"{permission_name}-roles"
            users_key = f"{permission_name}-users"
            
            if roles_key in perms or users_key in perms:
                return False, "Ya existe un permiso con ese nombre"
            
            updates = {
                f'perms/{roles_key}': 0,
                f'perms/{users_key}': 0
            }
            
            success = True
            for key, value in updates.items():
                if not update_server_data(guild_id, key, value):
                    success = False
                    break
            
            if success:
                return True, "Permiso personalizado creado correctamente"
            else:
                return False, "Error al crear el permiso personalizado"
                
        except Exception as e:
            print(f"Error creando permiso personalizado: {e}")
            import traceback
            traceback.print_exc()
            return False, "Error interno del servidor"
    
    def delete_custom_permission(self, guild_id, permission_name):
        try:
            server_data = get_server_data(guild_id)
            if not server_data:
                return False, "No se encontraron datos del servidor"
            
            if permission_name in ['admin', 'mg-srv']:
                return False, "No se pueden eliminar permisos del sistema"
            
            perms = server_data.get('perms', {})
            
            roles_key = f"{permission_name}-roles"
            users_key = f"{permission_name}-users"
            
            if roles_key not in perms and users_key not in perms:
                return False, "El permiso no existe"
            
            updates = {}
            if roles_key in perms:
                del perms[roles_key]
                updates['perms'] = perms
            
            if users_key in perms:
                del perms[users_key] 
                updates['perms'] = perms
            
            success = update_server_data(guild_id, 'perms', perms)
            
            if success:
                return True, "Permiso personalizado eliminado correctamente"
            else:
                return False, "Error al eliminar el permiso personalizado"
                
        except Exception as e:
            print(f"Error eliminando permiso personalizado: {e}")
            import traceback
            traceback.print_exc()
            return False, "Error interno del servidor"
    
    def get_guild_roles(self, guild_id):
        try:
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                return []
            
            return self._get_available_roles(guild)
        except Exception as e:
            print(f"Error obteniendo roles: {e}")
            import traceback
            traceback.print_exc()
            return []