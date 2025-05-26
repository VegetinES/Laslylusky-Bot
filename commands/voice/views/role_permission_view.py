import discord
from discord import ui
from ..permissions import add_role_to_channel
from ..utils import get_permission_description

class RolePermissionView(ui.View):
    def __init__(self, bot, channel, channel_data, parent_view):
        super().__init__(timeout=300)
        self.bot = bot
        self.channel = channel
        self.channel_data = channel_data
        self.parent_view = parent_view
    
    @ui.button(label="Añadir rol", style=discord.ButtonStyle.success)
    async def add_role(self, interaction: discord.Interaction, button: ui.Button):
        view = RoleSelectorView(self.bot, self.channel, self.channel_data, self)
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="Añadir rol",
                description="Selecciona un rol para añadirlo al canal.",
                color=discord.Color.blue()
            ),
            view=view
        )
    
    @ui.button(label="Ver roles", style=discord.ButtonStyle.secondary)
    async def view_roles(self, interaction: discord.Interaction, button: ui.Button):
        role_perms = self.channel_data.get("role_permissions", {})
        
        embed = discord.Embed(
            title="Roles con permisos",
            color=discord.Color.blue()
        )
        
        if not role_perms:
            embed.description = "No hay roles con permisos específicos en este canal."
        else:
            roles_list = []
            for role_id, level in role_perms.items():
                role = interaction.guild.get_role(int(role_id))
                if role:
                    desc = get_permission_description(level)
                    roles_list.append(f"{role.mention} - {desc}")
            
            if roles_list:
                embed.description = "\n".join(roles_list)
            else:
                embed.description = "No se encontraron roles con permisos."
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    @ui.button(label="Volver", style=discord.ButtonStyle.secondary)
    async def back_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="Gestión de permisos",
                description="¿Qué permisos deseas gestionar?",
                color=discord.Color.blue()
            ),
            view=self.parent_view
        )

class RoleSelectorView(ui.View):
    def __init__(self, bot, channel, channel_data, parent_view):
        super().__init__(timeout=300)
        self.bot = bot
        self.channel = channel
        self.channel_data = channel_data
        self.parent_view = parent_view
        self.selected_role = None
        
        options = []
        for role in channel.guild.roles:
            if role != channel.guild.default_role and not role.is_bot_managed() and not role.is_integration():
                options.append(
                    discord.SelectOption(
                        label=role.name,
                        description=f"ID: {role.id}",
                        value=str(role.id)
                    )
                )
        
        if options:
            select = ui.Select(
                placeholder="Selecciona un rol",
                options=options[:25],
                custom_id="role_select"
            )
            select.callback = self.select_callback
            self.add_item(select)
    
    async def select_callback(self, interaction: discord.Interaction):
        role_id = int(interaction.data["values"][0])
        role = interaction.guild.get_role(role_id)
        
        if not role:
            await interaction.response.send_message(
                "No se encontró el rol seleccionado.",
                ephemeral=True
            )
            return
        
        self.selected_role = role
        
        view = RolePermissionLevelView(self.bot, self.channel, self.channel_data, self.parent_view, self.selected_role)
        await interaction.response.edit_message(
            embed=discord.Embed(
                title=f"Permisos para {self.selected_role.name}",
                description="Selecciona el nivel de permisos para este rol.",
                color=discord.Color.blue()
            ),
            view=view
        )
    
    @ui.button(label="Volver", style=discord.ButtonStyle.secondary)
    async def back_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="Gestión de permisos de roles",
                description="Selecciona una acción para gestionar los permisos de roles.",
                color=discord.Color.blue()
            ),
            view=self.parent_view
        )

class RolePermissionLevelView(ui.View):
    def __init__(self, bot, channel, channel_data, parent_view, selected_role):
        super().__init__(timeout=300)
        self.bot = bot
        self.channel = channel
        self.channel_data = channel_data
        self.parent_view = parent_view
        self.selected_role = selected_role
    
    @ui.button(label="👁️ Espectador", style=discord.ButtonStyle.secondary)
    async def viewer_perm(self, interaction: discord.Interaction, button: ui.Button):
        result = await add_role_to_channel(self.channel, self.selected_role, interaction.guild.id, "viewer")
        
        if result:
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="Permisos actualizados",
                    description=f"Se han otorgado permisos de espectador al rol {self.selected_role.mention}.",
                    color=discord.Color.green()
                ),
                view=self.parent_view
            )
        else:
            await interaction.response.send_message(
                "Ocurrió un error al actualizar los permisos.",
                ephemeral=True
            )
    
    @ui.button(label="🛡️ Moderador", style=discord.ButtonStyle.primary)
    async def moderator_perm(self, interaction: discord.Interaction, button: ui.Button):
        result = await add_role_to_channel(self.channel, self.selected_role, interaction.guild.id, "moderator")
        
        if result:
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="Permisos actualizados",
                    description=f"Se han otorgado permisos de moderador al rol {self.selected_role.mention}.",
                    color=discord.Color.green()
                ),
                view=self.parent_view
            )
        else:
            await interaction.response.send_message(
                "Ocurrió un error al actualizar los permisos.",
                ephemeral=True
            )
    
    @ui.button(label="👑 Propietario adjunto", style=discord.ButtonStyle.success)
    async def coowner_perm(self, interaction: discord.Interaction, button: ui.Button):
        result = await add_role_to_channel(self.channel, self.selected_role, interaction.guild.id, "co-owner")
        
        if result:
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="Permisos actualizados",
                    description=f"Se han otorgado permisos de propietario adjunto al rol {self.selected_role.mention}.",
                    color=discord.Color.green()
                ),
                view=self.parent_view
            )
        else:
            await interaction.response.send_message(
                "Ocurrió un error al actualizar los permisos.",
                ephemeral=True
            )
    
    @ui.button(label="Volver", style=discord.ButtonStyle.secondary)
    async def back_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="Gestión de permisos de roles",
                description="Selecciona una acción para gestionar los permisos de roles.",
                color=discord.Color.blue()
            ),
            view=self.parent_view
        )