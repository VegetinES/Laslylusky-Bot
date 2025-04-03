import discord
from datetime import datetime

class PermissionsView(discord.ui.View):
    def __init__(self, author_id, guild_data):
        super().__init__(timeout=180)
        self.author_id = author_id
        self.guild_data = guild_data
        
        # Añadir selector para tipo de permisos
        options = [
            discord.SelectOption(label="Permisos de roles", value="roles", 
                                description="Ver permisos asignados a roles", 
                                emoji="👥"),
            discord.SelectOption(label="Permisos de usuarios", value="users", 
                                description="Ver permisos asignados a usuarios", 
                                emoji="👤"),
            discord.SelectOption(label="Volver atrás", value="back", 
                                description="Volver al menú principal", 
                                emoji="⬅️"),
            discord.SelectOption(label="Cancelar", value="cancel", 
                                description="Cancelar visualización", 
                                emoji="❌")
        ]
        
        self.perms_select = discord.ui.Select(
            placeholder="Selecciona tipo de permisos",
            options=options
        )
        self.perms_select.callback = self.perms_select_callback
        self.add_item(self.perms_select)
    
    async def interaction_check(self, interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "Solo la persona que ejecutó el comando puede usar estos controles.",
                ephemeral=True
            )
            return False
        return True
    
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        
        try:
            await self.message.edit(view=self)
        except:
            pass
    
    async def perms_select_callback(self, interaction):
        selection = self.perms_select.values[0]
        
        if selection == "back":
            from .configdata import ConfigDataMainView
            view = ConfigDataMainView(self.author_id, self.guild_data, interaction)
            await interaction.response.edit_message(
                content="Selecciona qué información quieres ver:",
                view=view,
                embed=None
            )
        elif selection == "cancel":
            for child in self.children:
                child.disabled = True
            
            await interaction.response.edit_message(
                content="Visualización de datos cancelada.",
                view=self,
                embed=None
            )
            self.stop()
        elif selection == "roles":
            embed = await create_roles_permissions_embed(self.guild_data, interaction)
            view = PermBackView(self.author_id, self.guild_data)
            await interaction.response.edit_message(
                content=None,
                embed=embed,
                view=view
            )
        elif selection == "users":
            embed = await create_users_permissions_embed(self.guild_data, interaction)
            view = PermBackView(self.author_id, self.guild_data)
            await interaction.response.edit_message(
                content=None,
                embed=embed,
                view=view
            )

class PermBackView(discord.ui.View):
    def __init__(self, author_id, guild_data):
        super().__init__(timeout=180)
        self.author_id = author_id
        self.guild_data = guild_data
        
        # Botón volver atrás
        self.back_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Volver atrás",
            custom_id="back_perms"
        )
        self.back_button.callback = self.back_callback
        self.add_item(self.back_button)
        
        # Botón cancelar
        self.cancel_button = discord.ui.Button(
            style=discord.ButtonStyle.danger,
            label="Cancelar",
            custom_id="cancel_perms"
        )
        self.cancel_button.callback = self.cancel_callback
        self.add_item(self.cancel_button)
    
    async def interaction_check(self, interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "Solo la persona que ejecutó el comando puede usar estos controles.",
                ephemeral=True
            )
            return False
        return True
    
    async def back_callback(self, interaction):
        view = PermissionsView(self.author_id, self.guild_data)
        await interaction.response.edit_message(
            content="Selecciona el tipo de permisos a visualizar:",
            view=view,
            embed=None
        )
    
    async def cancel_callback(self, interaction):
        for child in self.children:
            child.disabled = True
        
        await interaction.response.edit_message(
            content="Visualización de datos cancelada.",
            view=self,
            embed=None
        )
        self.stop()

async def create_roles_permissions_embed(guild_data, interaction):
    embed = discord.Embed(
        title=f"Permisos de roles en {interaction.guild.name}",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    
    perm_titles = {
        "admin": "Administrador",
        "mg-ch": "Gestionar canales",
        "mg-rl": "Gestionar roles",
        "mg-srv": "Gestionar servidor",
        "kick": "Expulsar miembros",
        "ban": "Banear miembros",
        "mute": "Mutear miembros",
        "deafen": "Ensordecer miembros",
        "mg-msg": "Gestionar mensajes",
        "warn": "Advertir miembros",
        "unwarn": "Quitar advertencias"
    }

    for base_perm in perm_titles:
        roles_key = f"{base_perm}-roles"
        if roles_key in guild_data["perms"]:
            roles = guild_data["perms"][roles_key]
            role_text = "ninguno"
            if roles != [0]:
                role_mentions = []
                for rid in roles:
                    if rid != 0:
                        role = interaction.guild.get_role(rid)
                        if role:
                            role_mentions.append(f"{role.mention} `[ID: {role.id}]`")
                role_text = "\n".join(role_mentions) if role_mentions else "ninguno"
            
            embed.add_field(name=perm_titles[base_perm], value=role_text, inline=False)
    
    embed.set_footer(text=f"Solicitado por {interaction.user.name}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
    return embed

async def create_users_permissions_embed(guild_data, interaction):
    embed = discord.Embed(
        title=f"Permisos de usuarios en {interaction.guild.name}",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    
    perm_titles = {
        "admin": "Administrador",
        "mg-ch": "Gestionar canales",
        "mg-rl": "Gestionar roles",
        "mg-srv": "Gestionar servidor",
        "kick": "Expulsar miembros",
        "ban": "Banear miembros",
        "mute": "Mutear miembros",
        "deafen": "Ensordecer miembros",
        "mg-msg": "Gestionar mensajes",
        "warn": "Advertir miembros",
        "unwarn": "Quitar advertencias"
    }

    for base_perm in perm_titles:
        users_key = f"{base_perm}-users"
        if users_key in guild_data["perms"]:
            users = guild_data["perms"][users_key]
            user_text = "ninguno"
            if users != [0]:
                user_mentions = []
                for uid in users:
                    if uid != 0:
                        member = interaction.guild.get_member(uid)
                        if member:
                            user_mentions.append(f"{member.mention} `[ID: {member.id}]`")
                user_text = "\n".join(user_mentions) if user_mentions else "ninguno"
            
            embed.add_field(name=perm_titles[base_perm], value=user_text, inline=False)
    
    embed.set_footer(text=f"Solicitado por {interaction.user.name}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
    return embed

async def show_permissions_data(interaction, guild_data, author_id):
    try:
        view = PermissionsView(author_id, guild_data)
        
        await interaction.response.edit_message(
            content="Selecciona el tipo de permisos a visualizar:",
            view=view,
            embed=None
        )
    except Exception as e:
        print(f"Error en show_permissions_data: {e}")
        await interaction.response.send_message(
            f"Error al mostrar los datos de permisos: {e}",
            ephemeral=True
        )