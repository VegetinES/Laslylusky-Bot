import discord

async def check_manage_permission(interaction, thread_id):
    try:
        thread = interaction.guild.get_thread(int(thread_id))
        if not thread or not thread.parent:
            return False
        
        parent_channel_id = str(thread.parent.id)
        from .database import get_ticket_data
        ticket_config = get_ticket_data(interaction.guild.id, parent_channel_id)
        
        if not ticket_config:
            # Si la configuración del ticket ya no existe, no hay permisos
            return None  # Valor especial para indicar que el ticket ya no existe
        
        if interaction.user.guild_permissions.administrator:
            return True
        
        user_roles = [role.id for role in interaction.user.roles]
        for role_id in ticket_config.get("permissions", {}).get("manage", {}).get("roles", []):
            if int(role_id) in user_roles:
                return True
        
        if str(interaction.user.id) in ticket_config.get("permissions", {}).get("manage", {}).get("users", []) or \
           interaction.user.id in ticket_config.get("permissions", {}).get("manage", {}).get("users", []):
            return True
        
        return False
    except Exception as e:
        print(f"Error al verificar permisos: {e}")
        return False