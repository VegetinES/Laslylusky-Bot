import discord
from database.get import get_server_data
from database.update import update_server_data
from .ticketsutils import get_ticket_config_state, CONFIG_STATE

async def show_tickets_perms(
    interaction: discord.Interaction,
    channel_id: str,
    permission: str,
    action: str,
    roles: str = None,
    users: str = None
):
    try:
        if not roles and not users:
            await interaction.response.send_message(
                "Debes proporcionar al menos un rol o usuario.",
                ephemeral=True
            )
            return

        config_state = get_ticket_config_state(interaction.guild.id, channel_id)
        if config_state == CONFIG_STATE["NO_CONFIGURADO"]:
            await interaction.response.send_message(
                "⚠️ **Error**: Este canal no está configurado como canal de tickets.\n\n"
                "Primero debes configurar el canal con el comando:\n"
                "`/config tickets canal canal_abrir_ticket:<canal> canal_logs:<canal> nombre_ticket:<nombre>`",
                ephemeral=True
            )
            return

        server_data = get_server_data(interaction.guild.id)
        if not server_data or "tickets" not in server_data or channel_id not in server_data["tickets"]:
            await interaction.response.send_message(
                "No hay configuración de tickets para este canal. Configura primero el canal con `/config tickets canal`.",
                ephemeral=True
            )
            return

        tickets_config = server_data["tickets"][channel_id]
        perms_config = tickets_config["perms"]

        perm_keys = {
            "manage": ["manage-roles", "manage-users"],
            "see": ["see-roles", "see-users"],
            "close": ["close-roles", "close-users"],
            "add-del-usr": ["add-del-usr-roles", "add-del-usr-users"]
        }
        
        if permission not in perm_keys:
            await interaction.response.send_message(
                f"Permiso no válido: {permission}",
                ephemeral=True
            )
            return
            
        roles_key, users_key = perm_keys[permission]

        roles_added = []
        roles_removed = []
        if roles:
            role_mentions = roles.split()
            for role_mention in role_mentions:
                role_id = None
                if role_mention.startswith('<@&') and role_mention.endswith('>'):
                    role_id = int(role_mention[3:-1])
                else:
                    try:
                        role_id = int(role_mention)
                    except ValueError:
                        continue
                        
                if role_id:
                    role = interaction.guild.get_role(role_id)
                    if role:
                        if action == "añadir":
                            if role_id not in perms_config[roles_key]:
                                if perms_config[roles_key] == [0]:
                                    perms_config[roles_key] = [role_id]
                                else:
                                    perms_config[roles_key].append(role_id)
                                roles_added.append(role.mention)
                        elif action == "eliminar":
                            if role_id in perms_config[roles_key]:
                                perms_config[roles_key].remove(role_id)
                                roles_removed.append(role.mention)
                                if not perms_config[roles_key]:
                                    perms_config[roles_key] = [0]

        users_added = []
        users_removed = []
        if users:
            user_mentions = users.split()
            for user_mention in user_mentions:
                user_id = None
                if user_mention.startswith('<@') and user_mention.endswith('>'):
                    user_id = int(user_mention.replace('!', '')[2:-1])
                else:
                    try:
                        user_id = int(user_mention)
                    except ValueError:
                        continue
                        
                if user_id:
                    user = await interaction.guild.fetch_member(user_id)
                    if user:
                        if action == "añadir":
                            if user_id not in perms_config[users_key]:
                                if perms_config[users_key] == [0]:
                                    perms_config[users_key] = [user_id]
                                else:
                                    perms_config[users_key].append(user_id)
                                users_added.append(user.mention)
                        elif action == "eliminar":
                            if user_id in perms_config[users_key]:
                                perms_config[users_key].remove(user_id)
                                users_removed.append(user.mention)
                                if not perms_config[users_key]:
                                    perms_config[users_key] = [0]

        if update_server_data(interaction.guild.id, f"tickets/{channel_id}/perms", perms_config):
            perm_descriptions = {
                "manage": "Gestionar tickets",
                "see": "Ver tickets",
                "close": "Cerrar tickets",
                "add-del-usr": "Añadir/eliminar usuarios"
            }
            
            action_text = "añadidos a" if action == "añadir" else "eliminados de"
            
            message_parts = [f"<:Si:825734135116070962> Permisos actualizados para: **{perm_descriptions[permission]}**"]
            
            if roles_added or roles_removed:
                roles_text = ", ".join(roles_added) if action == "añadir" else ", ".join(roles_removed)
                message_parts.append(f"**Roles {action_text}:** {roles_text}")
            
            if users_added or users_removed:
                users_text = ", ".join(users_added) if action == "añadir" else ", ".join(users_removed)
                message_parts.append(f"**Usuarios {action_text}:** {users_text}")

            manage_roles = perms_config.get("manage-roles", [0])
            manage_users = perms_config.get("manage-users", [0])
            has_manage_perms = (manage_roles != [0]) or (manage_users != [0])
            
            if has_manage_perms and permission == "manage" and action == "añadir":
                tickets_config = server_data["tickets"][channel_id]
                tickets_config["setup_stage"] = 2
                update_server_data(interaction.guild.id, f"tickets/{channel_id}", tickets_config)
                
                message_parts.append("\n⚠️ **Paso obligatorio siguiente**: Configura los mensajes con el comando:")
                message_parts.append(f"`/config tickets mensajes canal:{channel_id} tipo:ticket abierto título:<título> descripción:<descripción>`")
                message_parts.append("Y también:")
                message_parts.append(f"`/config tickets mensajes canal:{channel_id} tipo:abrir ticket título:<título> descripción:<descripción>`")
            
            await interaction.response.send_message("\n".join(message_parts), ephemeral=False)
        else:
            await interaction.response.send_message(
                "<:No:825734196256440340> Ocurrió un error al guardar los permisos.",
                ephemeral=True
            )
    
    except Exception as e:
        print(f"Error en show_tickets_perms: {e}")
        await interaction.response.send_message(
            f"<:No:825734196256440340> Ocurrió un error: {str(e)}",
            ephemeral=True
        )