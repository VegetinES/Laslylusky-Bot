import discord
from discord.ext import commands
from ..constants import PERMISSIONS_DESCRIPTIONS

class PermissionsView(discord.ui.View):
    def __init__(self, bot, ticket_config, ticket_channel, log_channel):
        super().__init__(timeout=300)
        self.bot = bot
        self.ticket_config = ticket_config
        self.ticket_channel = ticket_channel
        self.log_channel = log_channel
        
        if "permissions" not in self.ticket_config:
            self.ticket_config["permissions"] = {}
        
        for perm_type in ["manage", "view"]:
            if perm_type not in self.ticket_config["permissions"]:
                self.ticket_config["permissions"][perm_type] = {
                    "roles": [],
                    "users": []
                }
            if "roles" not in self.ticket_config["permissions"][perm_type]:
                self.ticket_config["permissions"][perm_type]["roles"] = []
            if "users" not in self.ticket_config["permissions"][perm_type]:
                self.ticket_config["permissions"][perm_type]["users"] = []
        
        manage_btn = discord.ui.Button(
            style=discord.ButtonStyle.primary,
            label="Gestionar Tickets",
            emoji="🔑",
            custom_id="manage_perm",
            row=0
        )
        manage_btn.callback = self.manage_callback
        self.add_item(manage_btn)
        
        view_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Ver Tickets",
            emoji="👁️",
            custom_id="view_perm",
            row=0
        )
        view_btn.callback = self.view_callback
        self.add_item(view_btn)
        
        back_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Volver",
            emoji="⬅️",
            custom_id="back_to_edit",
            row=1
        )
        back_btn.callback = self.back_callback
        self.add_item(back_btn)
        
        cancel_btn = discord.ui.Button(
            style=discord.ButtonStyle.danger,
            label="Cancelar",
            emoji="❌",
            custom_id="cancel_perms",
            row=1
        )
        cancel_btn.callback = self.cancel_callback
        self.add_item(cancel_btn)
    
    async def manage_callback(self, interaction: discord.Interaction):
        try:
            await self.show_permission_config(interaction, "manage")
        except Exception as e:
            print(f"Error en manage_callback: {e}")
            await interaction.response.send_message(
                f"<:No:825734196256440340> Error al mostrar configuración de permisos: {str(e)}",
                ephemeral=True
            )
    
    async def view_callback(self, interaction: discord.Interaction):
        try:
            await self.show_permission_config(interaction, "view")
        except Exception as e:
            print(f"Error en view_callback: {e}")
            await interaction.response.send_message(
                f"<:No:825734196256440340> Error al mostrar configuración de permisos: {str(e)}",
                ephemeral=True
            )
    
    async def show_permission_config(self, interaction, perm_type):
        try:
            if "permissions" not in self.ticket_config:
                self.ticket_config["permissions"] = {}
            
            if perm_type not in self.ticket_config["permissions"]:
                self.ticket_config["permissions"][perm_type] = {
                    "roles": [],
                    "users": []
                }
            
            if "roles" not in self.ticket_config["permissions"][perm_type]:
                self.ticket_config["permissions"][perm_type]["roles"] = []
            
            if "users" not in self.ticket_config["permissions"][perm_type]:
                self.ticket_config["permissions"][perm_type]["users"] = []
            
            perm_config = self.ticket_config["permissions"][perm_type]
            
            embed = discord.Embed(
                title=f"Permisos: {PERMISSIONS_DESCRIPTIONS[perm_type]['name']}",
                description=PERMISSIONS_DESCRIPTIONS[perm_type]["description"],
                color=0x3498db
            )
            
            roles_text = "Ninguno"
            if perm_config["roles"] and len(perm_config["roles"]) > 0:
                roles_mentions = []
                for role_id in perm_config["roles"]:
                    role = interaction.guild.get_role(int(role_id))
                    if role:
                        roles_mentions.append(f"{role.mention} `[ID: {role.id}]`")
                if roles_mentions:
                    roles_text = "\n".join(roles_mentions)
            
            users_text = "Ninguno"
            if perm_config["users"] and len(perm_config["users"]) > 0:
                users_mentions = []
                for user_id in perm_config["users"]:
                    try:
                        user = await interaction.guild.fetch_member(int(user_id))
                        if user:
                            users_mentions.append(f"{user.mention} `[ID: {user.id}]`")
                    except:
                        pass
                if users_mentions:
                    users_text = "\n".join(users_mentions)
            
            embed.add_field(name="Roles", value=roles_text, inline=False)
            embed.add_field(name="Usuarios", value=users_text, inline=False)
            
            view = PermissionConfigView(self.bot, self.ticket_config, self.ticket_channel, self.log_channel, perm_type)
            
            await interaction.response.edit_message(
                embed=embed,
                view=view
            )
        except Exception as e:
            print(f"Error en show_permission_config: {e}")
            error_message = f"Error al mostrar configuración de permisos: {str(e)}\n"
            error_message += f"Estructura de ticket_config: {self.ticket_config}"
            print(error_message)
            await interaction.response.send_message(
                f"<:No:825734196256440340> Error al mostrar configuración de permisos: {str(e)}",
                ephemeral=True
            )
    
    async def back_callback(self, interaction: discord.Interaction):
        try:
            from .edit_view import TicketEditView
            
            view = TicketEditView(self.bot, self.ticket_config, self.ticket_channel, self.log_channel)
            
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="Configurar Ticket",
                    description=f"Configura el ticket para el canal {self.ticket_channel.mention}",
                    color=0x3498db
                ),
                view=view
            )
        except Exception as e:
            print(f"Error en back_callback: {e}")
            await interaction.response.send_message(
                f"<:No:825734196256440340> Error al volver: {str(e)}",
                ephemeral=True
            )
    
    async def cancel_callback(self, interaction: discord.Interaction):
        try:
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="Configuración Cancelada",
                    description="<:No:825734196256440340> Has cancelado la configuración de permisos.",
                    color=0xe74c3c
                ),
                view=None
            )
        except Exception as e:
            print(f"Error en cancel_callback: {e}")
            await interaction.response.send_message(
                f"<:No:825734196256440340> Error al cancelar: {str(e)}",
                ephemeral=True
            )

class PermissionConfigView(discord.ui.View):
    def __init__(self, bot, ticket_config, ticket_channel, log_channel, perm_type):
        super().__init__(timeout=300)
        self.bot = bot
        self.ticket_config = ticket_config
        self.ticket_channel = ticket_channel
        self.log_channel = log_channel
        self.perm_type = perm_type
        self.current_role_page = 0
        
        add_role_btn = discord.ui.Button(
            style=discord.ButtonStyle.success,
            label="Añadir Rol",
            emoji="➕",
            custom_id="add_role",
            row=0
        )
        add_role_btn.callback = self.add_role_callback
        self.add_item(add_role_btn)
        
        remove_role_btn = discord.ui.Button(
            style=discord.ButtonStyle.danger,
            label="Eliminar Rol",
            emoji="➖",
            custom_id="remove_role",
            row=0
        )
        remove_role_btn.callback = self.remove_role_callback
        self.add_item(remove_role_btn)
        
        add_user_btn = discord.ui.Button(
            style=discord.ButtonStyle.success,
            label="Añadir Usuario",
            emoji="➕",
            custom_id="add_user",
            row=1
        )
        add_user_btn.callback = self.add_user_callback
        self.add_item(add_user_btn)
        
        remove_user_btn = discord.ui.Button(
            style=discord.ButtonStyle.danger,
            label="Eliminar Usuario",
            emoji="➖",
            custom_id="remove_user",
            row=1
        )
        remove_user_btn.callback = self.remove_user_callback
        self.add_item(remove_user_btn)
        
        back_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Volver",
            emoji="⬅️",
            custom_id="back_to_perms",
            row=2
        )
        back_btn.callback = self.back_callback
        self.add_item(back_btn)
        
        save_btn = discord.ui.Button(
            style=discord.ButtonStyle.primary,
            label="Guardar Cambios",
            emoji="💾",
            custom_id="save_perms",
            row=2
        )
        save_btn.callback = self.save_callback
        self.add_item(save_btn)
    
    async def add_role_callback(self, interaction: discord.Interaction):
        try:
            options = []
            count = 0
            
            for role in interaction.guild.roles:
                if role.id != interaction.guild.default_role.id and count < 25:
                    if role.id not in self.ticket_config["permissions"][self.perm_type]["roles"]:
                        options.append(
                            discord.SelectOption(
                                label=role.name[:25],
                                value=str(role.id),
                                description=f"ID: {role.id}"[:50]
                            )
                        )
                        count += 1
            
            if options:
                select = discord.ui.Select(
                    placeholder="Selecciona un rol para añadir",
                    options=options,
                    custom_id="select_role"
                )
                
                async def role_select_callback(select_interaction):
                    try:
                        role_id = int(select_interaction.data["values"][0])
                        
                        if role_id not in self.ticket_config["permissions"][self.perm_type]["roles"]:
                            self.ticket_config["permissions"][self.perm_type]["roles"].append(role_id)
                        
                        await self.update_permission_view(select_interaction)
                    except Exception as e:
                        print(f"Error en role_select_callback: {e}")
                        await select_interaction.response.send_message(
                            f"<:No:825734196256440340> Error al seleccionar rol: {str(e)}",
                            ephemeral=True
                        )
                
                select.callback = role_select_callback
                
                temp_view = discord.ui.View(timeout=60)
                temp_view.add_item(select)
                
                back_btn = discord.ui.Button(
                    style=discord.ButtonStyle.secondary,
                    label="Cancelar",
                    custom_id="cancel_add_role"
                )
                
                async def back_callback(btn_interaction):
                    await self.update_permission_view(btn_interaction)
                
                back_btn.callback = back_callback
                temp_view.add_item(back_btn)
                
                await interaction.response.edit_message(
                    content="Selecciona un rol para añadir:",
                    embed=None,
                    view=temp_view
                )
            else:
                await interaction.response.send_message(
                    "<:No:825734196256440340> No hay roles disponibles para añadir o todos ya han sido añadidos.",
                    ephemeral=True
                )
        except Exception as e:
            print(f"Error en add_role_callback: {e}")
            await interaction.response.send_message(
                f"<:No:825734196256440340> Error al mostrar roles: {str(e)}",
                ephemeral=True
            )
    
    def create_roles_select(self, all_roles, page, interaction):
        start_idx = page * 25
        end_idx = min(start_idx + 25, len(all_roles))
        current_roles = all_roles[start_idx:end_idx]
        
        options = []
        for role in current_roles:
            options.append(
                discord.SelectOption(
                    label=role.name,
                    value=str(role.id),
                    description=f"Rol ID: {role.id}"
                )
            )
        
        select = discord.ui.Select(
            placeholder="Selecciona un rol para añadir",
            options=options,
            custom_id="select_role"
        )
        
        async def role_select_callback(select_interaction):
            role_id = int(select_interaction.data["values"][0])
            
            if role_id not in self.ticket_config["permissions"][self.perm_type]["roles"]:
                self.ticket_config["permissions"][self.perm_type]["roles"].append(role_id)
            
            await self.update_permission_view(select_interaction)
        
        select.callback = role_select_callback
        return select
    
    async def remove_role_callback(self, interaction: discord.Interaction):
        roles = self.ticket_config["permissions"][self.perm_type]["roles"]
        
        if not roles:
            await interaction.response.send_message(
                "<:No:825734196256440340> No hay roles configurados para este permiso.",
                ephemeral=True
            )
            return
        
        configured_roles = []
        for role_id in roles:
            role = interaction.guild.get_role(int(role_id))
            if role:
                configured_roles.append(role)
        
        if not configured_roles:
            await interaction.response.send_message(
                "<:No:825734196256440340> No se encontraron roles configurados.",
                ephemeral=True
            )
            return
        
        total_pages = (len(configured_roles) - 1) // 25 + 1
        view = discord.ui.View()
        
        options = []
        for role in configured_roles[:25]: 
            options.append(
                discord.SelectOption(
                    label=role.name,
                    value=str(role.id),
                    description=f"Rol ID: {role.id}"
                )
            )
        
        select = discord.ui.Select(
            placeholder="Selecciona un rol para eliminar",
            options=options,
            custom_id="select_role_remove"
        )
        
        async def role_select_callback(select_interaction):
            role_id = int(select_interaction.data["values"][0])
            
            if role_id in self.ticket_config["permissions"][self.perm_type]["roles"]:
                self.ticket_config["permissions"][self.perm_type]["roles"].remove(role_id)
            
            await self.update_permission_view(select_interaction)
        
        select.callback = role_select_callback
        view.add_item(select)
        
        if total_pages > 1:
            prev_btn = discord.ui.Button(
                style=discord.ButtonStyle.secondary,
                label="◀️ Anterior",
                custom_id="prev_remove_page",
                disabled=True,
                row=1
            )
            
            next_btn = discord.ui.Button(
                style=discord.ButtonStyle.secondary,
                label="Siguiente ▶️",
                custom_id="next_remove_page",
                disabled=False,
                row=1
            )
            
            current_page = [0]
            
            async def prev_remove_callback(btn_interaction):
                current_page[0] -= 1
                if current_page[0] < 0:
                    current_page[0] = 0
                
                await update_remove_page(btn_interaction)
            
            async def next_remove_callback(btn_interaction):
                current_page[0] += 1
                if current_page[0] >= total_pages:
                    current_page[0] = total_pages - 1
                
                await update_remove_page(btn_interaction)
            
            async def update_remove_page(btn_interaction):
                page = current_page[0]
                start_idx = page * 25
                end_idx = min(start_idx + 25, len(configured_roles))
                
                new_options = []
                for role in configured_roles[start_idx:end_idx]:
                    new_options.append(
                        discord.SelectOption(
                            label=role.name,
                            value=str(role.id),
                            description=f"Rol ID: {role.id}"
                        )
                    )
                
                for item in view.children:
                    if isinstance(item, discord.ui.Select):
                        item.options = new_options
                        break
                
                for item in view.children:
                    if isinstance(item, discord.ui.Button):
                        if item.custom_id == "prev_remove_page":
                            item.disabled = page == 0
                        elif item.custom_id == "next_remove_page":
                            item.disabled = page >= total_pages - 1
                
                await btn_interaction.response.edit_message(
                    content=f"Selecciona un rol para eliminar de permisos de {PERMISSIONS_DESCRIPTIONS[self.perm_type]['name']} (Página {page+1}/{total_pages})",
                    view=view
                )
            
            prev_btn.callback = prev_remove_callback
            next_btn.callback = next_remove_callback
            
            view.add_item(prev_btn)
            view.add_item(next_btn)
        
        cancel_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Cancelar",
            custom_id="cancel_remove_role",
            row=2
        )
        
        async def cancel_callback(btn_interaction):
            await self.update_permission_view(btn_interaction)
        
        cancel_btn.callback = cancel_callback
        view.add_item(cancel_btn)
        
        await interaction.response.edit_message(
            content=f"Selecciona un rol para eliminar de permisos de {PERMISSIONS_DESCRIPTIONS[self.perm_type]['name']}" + 
                   (f" (Página 1/{total_pages})" if total_pages > 1 else ""),
            embed=None,
            view=view
        )
    
    async def add_user_callback(self, interaction: discord.Interaction):
        view = discord.ui.View()
        
        user_select = discord.ui.UserSelect(
            placeholder="Selecciona un usuario para añadir",
            min_values=1,
            max_values=1,
            custom_id="user_select_add"
        )
        
        async def user_select_callback(select_interaction):
            user_id = select_interaction.data["values"][0]
            user = await interaction.guild.fetch_member(int(user_id))
            
            if not user:
                await select_interaction.response.send_message(
                    "<:No:825734196256440340> No se encontró al usuario en el servidor.",
                    ephemeral=True
                )
                return
            
            if user_id not in self.ticket_config["permissions"][self.perm_type]["users"]:
                self.ticket_config["permissions"][self.perm_type]["users"].append(int(user_id))
            
            await self.update_permission_view(select_interaction)
        
        user_select.callback = user_select_callback
        view.add_item(user_select)
        
        cancel_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Cancelar",
            custom_id="cancel_add_user"
        )
        
        async def cancel_callback(btn_interaction):
            await self.update_permission_view(btn_interaction)
        
        cancel_btn.callback = cancel_callback
        view.add_item(cancel_btn)
        
        await interaction.response.edit_message(
            content=f"Selecciona un usuario para añadir a permisos de {PERMISSIONS_DESCRIPTIONS[self.perm_type]['name']}",
            embed=None,
            view=view
        )
    
    async def remove_user_callback(self, interaction: discord.Interaction):
        users = self.ticket_config["permissions"][self.perm_type]["users"]
        
        if not users:
            await interaction.response.send_message(
                "<:No:825734196256440340> No hay usuarios configurados para este permiso.",
                ephemeral=True
            )
            return
        
        view = discord.ui.View()
        
        user_select = discord.ui.UserSelect(
            placeholder="Selecciona un usuario para eliminar",
            min_values=1,
            max_values=1,
            custom_id="user_select_remove"
        )
        
        async def user_select_callback(select_interaction):
            user_id = int(select_interaction.data["values"][0])
            
            if user_id not in self.ticket_config["permissions"][self.perm_type]["users"]:
                await select_interaction.response.send_message(
                    f"<:No:825734196256440340> El usuario seleccionado no tiene configurado el permiso de {PERMISSIONS_DESCRIPTIONS[self.perm_type]['name']}.",
                    ephemeral=True
                )
                return
            
            self.ticket_config["permissions"][self.perm_type]["users"].remove(user_id)
            await self.update_permission_view(select_interaction)
        
        user_select.callback = user_select_callback
        view.add_item(user_select)
        
        info_text = "Usuarios con permisos configurados:\n"
        user_mentions = []
        for user_id in users:
            try:
                user = await interaction.guild.fetch_member(int(user_id))
                if user:
                    user_mentions.append(f"{user.mention} ({user.id})")
            except:
                user_mentions.append(f"Usuario ID: {user_id}")
        
        if user_mentions:
            info_text += "\n".join(user_mentions)
        else:
            info_text = "No hay usuarios configurados para mostrar."
        
        cancel_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Cancelar",
            custom_id="cancel_remove_user"
        )
        
        async def cancel_callback(btn_interaction):
            await self.update_permission_view(btn_interaction)
        
        cancel_btn.callback = cancel_callback
        view.add_item(cancel_btn)
        
        await interaction.response.edit_message(
            content=f"Selecciona un usuario para eliminar de permisos de {PERMISSIONS_DESCRIPTIONS[self.perm_type]['name']}\n\n{info_text}",
            embed=None,
            view=view
        )
    
    async def update_permission_view(self, interaction):
        perm_config = self.ticket_config["permissions"][self.perm_type]
        
        embed = discord.Embed(
            title=f"Permisos: {PERMISSIONS_DESCRIPTIONS[self.perm_type]['name']}",
            description=PERMISSIONS_DESCRIPTIONS[self.perm_type]["description"],
            color=0x3498db
        )
        
        roles_text = "Ninguno"
        if perm_config["roles"]:
            roles_mentions = []
            for role_id in perm_config["roles"]:
                role = interaction.guild.get_role(int(role_id))
                if role:
                    roles_mentions.append(f"{role.mention} `[ID: {role.id}]`")
            if roles_mentions:
                roles_text = "\n".join(roles_mentions)
        
        users_text = "Ninguno"
        if perm_config["users"]:
            users_mentions = []
            for user_id in perm_config["users"]:
                try:
                    user = await interaction.guild.fetch_member(int(user_id))
                    if user:
                        users_mentions.append(f"{user.mention} `[ID: {user.id}]`")
                except:
                    pass
            if users_mentions:
                users_text = "\n".join(users_mentions)
        
        embed.add_field(name="Roles", value=roles_text, inline=False)
        embed.add_field(name="Usuarios", value=users_text, inline=False)
        
        await interaction.response.edit_message(
            content=None,
            embed=embed,
            view=self
        )
    
    async def back_callback(self, interaction: discord.Interaction):
        from .permissions_view import PermissionsView
        
        view = PermissionsView(self.bot, self.ticket_config, self.ticket_channel, self.log_channel)
        
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="Gestionar Permisos",
                description=f"Configura los permisos para los tickets en {self.ticket_channel.mention}",
                color=0x3498db
            ),
            view=view
        )
    
    async def save_callback(self, interaction: discord.Interaction):
        perm_config = self.ticket_config["permissions"][self.perm_type]
        
        embed = discord.Embed(
            title=f"<:Si:825734135116070962> Permisos Guardados",
            description=f"Los permisos de '{PERMISSIONS_DESCRIPTIONS[self.perm_type]['name']}' han sido guardados correctamente.",
            color=0x2ecc71
        )
        
        roles_text = "Ninguno"
        if perm_config["roles"]:
            roles_mentions = []
            for role_id in perm_config["roles"]:
                role = interaction.guild.get_role(int(role_id))
                if role:
                    roles_mentions.append(f"{role.mention} `[ID: {role.id}]`")
            if roles_mentions:
                roles_text = "\n".join(roles_mentions)
        
        users_text = "Ninguno"
        if perm_config["users"]:
            users_mentions = []
            for user_id in perm_config["users"]:
                try:
                    user = await interaction.guild.fetch_member(int(user_id))
                    if user:
                        users_mentions.append(f"{user.mention} `[ID: {user.id}]`")
                except:
                    pass
            if users_mentions:
                users_text = "\n".join(users_mentions)
        
        embed.add_field(name="Roles", value=roles_text, inline=False)
        embed.add_field(name="Usuarios", value=users_text, inline=False)
        
        from .permissions_view import PermissionsView
        view = PermissionsView(self.bot, self.ticket_config, self.ticket_channel, self.log_channel)
        
        await interaction.response.edit_message(
            embed=embed,
            view=view
        )