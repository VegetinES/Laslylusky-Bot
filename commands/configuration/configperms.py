import discord
from discord import app_commands
from database.get import get_server_data, get_specific_field
from database.update import update_server_data
from typing import Optional, Union

async def show_config_perms(
    interaction: discord.Interaction, 
    permiso: str, 
    accion: str, 
    roles: Optional[str] = None, 
    usuarios: Optional[str] = None
):
    guild_id = interaction.guild.id
    server_data = get_server_data(guild_id)
    
    if not server_data:
        await interaction.response.send_message(
            "No se encontraron datos para este servidor. Ejecuta `</config update:1348248454610161751>` para inicializar la configuración.",
            ephemeral=True
        )
        return
    
    roles_list = []
    usuarios_list = []
    
    if roles:
        role_mentions = roles.split()
        for role_mention in role_mentions:
            if role_mention.startswith('<@&') and role_mention.endswith('>'):
                try:
                    role_id = int(role_mention[3:-1])
                    role = interaction.guild.get_role(role_id)
                    if role and role.name.lower() not in ['everyone', '@everyone', 'here', '@here']:
                        roles_list.append(role)
                except ValueError:
                    pass
            else:
                try:
                    role_id = int(role_mention)
                    role = interaction.guild.get_role(role_id)
                    if role:
                        roles_list.append(role)
                except ValueError:
                    roles_by_name = [r for r in interaction.guild.roles if r.name.lower() == role_mention.lower()]
                    roles_list.extend(roles_by_name)
    
    if usuarios:
        user_mentions = usuarios.split()
        for user_mention in user_mentions:
            if user_mention.startswith('<@') and user_mention.endswith('>'):
                try:
                    user_id = int(user_mention[2:-1].replace('!', ''))
                    user = interaction.guild.get_member(user_id)
                    if user:
                        usuarios_list.append(user)
                except ValueError:
                    pass
            else:
                try:
                    user_id = int(user_mention)
                    user = interaction.guild.get_member(user_id)
                    if user:
                        usuarios_list.append(user)
                except ValueError:
                    users_by_name = [u for u in interaction.guild.members if u.name.lower() == user_mention.lower()]
                    usuarios_list.extend(users_by_name)
    
    if not roles_list and not usuarios_list:
        await interaction.response.send_message(
            "Debes proporcionar al menos un rol o un usuario válido.",
            ephemeral=True
        )
        return

    perms = server_data.get('perms', {})
    roles_path = f"{permiso}-roles"
    users_path = f"{permiso}-users"
    
    if roles_path not in perms and users_path not in perms:
        unique_perms = set()
        for key in perms.keys():
            if key.endswith('-roles') or key.endswith('-users'):
                base_perm = key.rsplit('-', 1)[0]
                unique_perms.add(base_perm)
        
        await interaction.response.send_message(
            f"El permiso '{permiso}' no existe. Los permisos disponibles son: {', '.join(sorted(unique_perms))}",
            ephemeral=True
        )
        return

    roles_ids = [role.id for role in roles_list if role.name.lower() not in ['everyone', '@everyone', 'here', '@here']]
    usuarios_ids = [usuario.id for usuario in usuarios_list]
    
    if accion == "añadir":
        await add_permissions(interaction, permiso, roles_ids, usuarios_ids, server_data)
    elif accion == "eliminar":
        await remove_permissions(interaction, permiso, roles_ids, usuarios_ids, server_data)
    else:
        await interaction.response.send_message(
            "Acción no válida. Las acciones permitidas son 'añadir' o 'eliminar'.",
            ephemeral=True
        )

async def add_permissions(interaction, permiso, roles_ids, usuarios_ids, server_data):
    perms = server_data.get('perms', {})

    roles_path = f"{permiso}-roles"
    users_path = f"{permiso}-users"

    has_roles = roles_path in perms
    has_users = users_path in perms
    
    if not has_roles and not has_users:
        await interaction.response.send_message(
            f"No se encontró el permiso '{permiso}' en la configuración.",
            ephemeral=True
        )
        return
    
    current_roles_ids = perms.get(roles_path, [])
    if current_roles_ids == 0:
        current_roles_ids = []
    
    current_users_ids = perms.get(users_path, [])
    if current_users_ids == 0:
        current_users_ids = []

    if roles_ids:
        for role_id in roles_ids:
            if role_id not in current_roles_ids:
                current_roles_ids.append(role_id)
    
    if usuarios_ids:
        for user_id in usuarios_ids:
            if user_id not in current_users_ids:
                current_users_ids.append(user_id)

    updates = {}
    if roles_ids and has_roles:
        updates[roles_path] = current_roles_ids
    if usuarios_ids and has_users:
        updates[users_path] = current_users_ids
    
    if update_server_data(interaction.guild.id, 'perms', updates):
        confirmation = []
        if roles_ids and has_roles:
            role_mentions = [f"<@&{role_id}>" for role_id in roles_ids]
            confirmation.append(f"Roles añadidos: {', '.join(role_mentions)}")
        
        if usuarios_ids and has_users:
            user_mentions = [f"<@{user_id}>" for user_id in usuarios_ids]
            confirmation.append(f"Usuarios añadidos: {', '.join(user_mentions)}")
        
        await interaction.response.send_message(
            f"Los permisos '{permiso}' han sido actualizados.\n" + "\n".join(confirmation),
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "Hubo un error al actualizar los permisos. Por favor, inténtalo de nuevo.",
            ephemeral=True
        )

async def remove_permissions(interaction, permiso, roles_ids, usuarios_ids, server_data):
    perms = server_data.get('perms', {})

    roles_path = f"{permiso}-roles"
    users_path = f"{permiso}-users"

    has_roles = roles_path in perms
    has_users = users_path in perms
    
    if not has_roles and not has_users:
        await interaction.response.send_message(
            f"No se encontró el permiso '{permiso}' en la configuración.",
            ephemeral=True
        )
        return

    current_roles_ids = perms.get(roles_path, [])
    if current_roles_ids == 0: 
        current_roles_ids = []
    
    current_users_ids = perms.get(users_path, [])
    if current_users_ids == 0:
        current_users_ids = []
    
    roles_removed = []
    users_removed = []
    
    if roles_ids and has_roles:
        roles_removed = [role_id for role_id in roles_ids if role_id in current_roles_ids]
        current_roles_ids = [role_id for role_id in current_roles_ids if role_id not in roles_ids]
    
    if usuarios_ids and has_users:
        users_removed = [user_id for user_id in usuarios_ids if user_id in current_users_ids]
        current_users_ids = [user_id for user_id in current_users_ids if user_id not in usuarios_ids]

    updates = {}
    if roles_ids and has_roles:
        updates[roles_path] = current_roles_ids if current_roles_ids else 0
    if usuarios_ids and has_users:
        updates[users_path] = current_users_ids if current_users_ids else 0
    
    if update_server_data(interaction.guild.id, 'perms', updates):
        confirmation = []
        if roles_removed:
            role_mentions = [f"<@&{role_id}>" for role_id in roles_removed]
            confirmation.append(f"Roles eliminados: {', '.join(role_mentions)}")
        
        if users_removed:
            user_mentions = [f"<@{user_id}>" for user_id in users_removed]
            confirmation.append(f"Usuarios eliminados: {', '.join(user_mentions)}")
        
        if not roles_removed and not users_removed:
            confirmation.append("No se encontraron los roles o usuarios especificados para eliminar.")
        
        await interaction.response.send_message(
            f"Los permisos '{permiso}' han sido actualizados.\n" + "\n".join(confirmation),
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "Hubo un error al actualizar los permisos. Por favor, inténtalo de nuevo.",
            ephemeral=True
        )

async def permission_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    guild_id = interaction.guild.id
    server_data = get_server_data(guild_id)
    
    if not server_data or 'perms' not in server_data:
        return []
    
    perms = server_data.get('perms', {})
    unique_perms = set()
    for key in perms.keys():
        if key.endswith('-roles') or key.endswith('-users'):
            base_perm = key.rsplit('-', 1)[0]
            unique_perms.add(base_perm)
    
    return [
        app_commands.Choice(name=perm, value=perm)
        for perm in unique_perms if current.lower() in perm.lower()
    ][:25]

async def users_roles_with_permission_autocomplete(interaction: discord.Interaction, current: str, permission: str, is_role: bool) -> list[app_commands.Choice[str]]:
    guild_id = interaction.guild.id
    server_data = get_server_data(guild_id)
    
    if not server_data or 'perms' not in server_data:
        return []
    
    perms = server_data.get('perms', {})
    
    suffix = '-roles' if is_role else '-users'
    path = f"{permission}{suffix}"
    
    if path not in perms:
        return []
    
    ids = perms.get(path, [])
    if ids == 0:
        return []
    
    result = []
    for id_value in ids:
        item = None
        if is_role:
            item = interaction.guild.get_role(id_value)
            if item and current.lower() in item.name.lower():
                result.append(app_commands.Choice(name=item.name, value=str(id_value)))
        else:
            try:
                member = await interaction.guild.fetch_member(id_value)
                if member and current.lower() in member.display_name.lower():
                    result.append(app_commands.Choice(name=member.display_name, value=str(id_value)))
            except:
                pass
    
    return result[:25]

async def roles_with_permission_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    permission = None
    for option in interaction.data.get('options', []):
        if option.get('name') == 'permiso':
            permission = option.get('value')
            break
    
    if not permission:
        return []
    
    return await users_roles_with_permission_autocomplete(interaction, current, permission, True)

async def users_with_permission_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    permission = None
    for option in interaction.data.get('options', []):
        if option.get('name') == 'permiso':
            permission = option.get('value')
            break
    
    if not permission:
        return []
    
    return await users_roles_with_permission_autocomplete(interaction, current, permission, False)