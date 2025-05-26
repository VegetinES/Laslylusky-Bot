import discord
from discord import ui
from ..permissions import add_user_to_channel, remove_user_from_channel
from ..utils import get_permission_description

class UserPermissionView(ui.View):
    def __init__(self, bot, channel, channel_data, parent_view):
        super().__init__(timeout=300)
        self.bot = bot
        self.channel = channel
        self.channel_data = channel_data
        self.parent_view = parent_view
    
    @ui.button(label="Añadir usuario", style=discord.ButtonStyle.success)
    async def add_user(self, interaction: discord.Interaction, button: ui.Button):
        add_view = ui.View(timeout=60)
        user_select = ui.UserSelect(
            placeholder="Selecciona un usuario para añadir",
            min_values=1,
            max_values=1
        )
        
        async def user_select_callback(select_interaction):
            selected_user = select_interaction.guild.get_member(int(select_interaction.data["values"][0]))
            
            if not selected_user:
                await select_interaction.response.send_message(
                    "❌ No se encontró el usuario seleccionado.",
                    ephemeral=True
                )
                return
                
            view = PermissionLevelView(self.bot, self.channel, self.channel_data, self, selected_user)
            await select_interaction.response.edit_message(
                content=None,
                embed=discord.Embed(
                    title=f"Permisos para {selected_user.display_name}",
                    description="Selecciona el nivel de permisos para este usuario.",
                    color=discord.Color.blue()
                ),
                view=view
            )
        
        user_select.callback = user_select_callback
        add_view.add_item(user_select)
        
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="Añadir usuario",
                description="Selecciona un usuario para añadirlo al canal.",
                color=discord.Color.blue()
            ),
            view=add_view
        )
    
    @ui.button(label="Eliminar usuario", style=discord.ButtonStyle.danger)
    async def remove_user(self, interaction: discord.Interaction, button: ui.Button):
        user_perms = self.channel_data.get("user_permissions", {})
        if not user_perms:
            await interaction.response.send_message(
                "No hay usuarios con permisos específicos en este canal.",
                ephemeral=True
            )
            return
        
        view = UserRemoveView(self.bot, self.channel, self.channel_data, self)
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="Eliminar usuario",
                description="Selecciona un usuario para eliminar sus permisos del canal.",
                color=discord.Color.blue()
            ),
            view=view
        )
    
    @ui.button(label="Ver usuarios", style=discord.ButtonStyle.secondary)
    async def view_users(self, interaction: discord.Interaction, button: ui.Button):
        user_perms = self.channel_data.get("user_permissions", {})
        
        embed = discord.Embed(
            title="Usuarios con permisos",
            color=discord.Color.blue()
        )
        
        if not user_perms:
            embed.description = "No hay usuarios con permisos específicos en este canal."
        else:
            users_list = []
            for user_id, level in user_perms.items():
                user = interaction.guild.get_member(int(user_id))
                if user:
                    desc = get_permission_description(level)
                    users_list.append(f"{user.mention} - {desc}")
            
            if users_list:
                embed.description = "\n".join(users_list)
            else:
                embed.description = "No se encontraron usuarios con permisos."
        
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

class UserRemoveView(ui.View):
    def __init__(self, bot, channel, channel_data, parent_view):
        super().__init__(timeout=300)
        self.bot = bot
        self.channel = channel
        self.channel_data = channel_data
        self.parent_view = parent_view
        
        options = []
        user_perms = self.channel_data.get("user_permissions", {})
        
        for user_id, level in user_perms.items():
            user = channel.guild.get_member(int(user_id))
            if user:
                options.append(
                    discord.SelectOption(
                        label=user.display_name,
                        description=f"ID: {user.id}",
                        value=str(user.id)
                    )
                )
        
        if options:
            select = ui.Select(
                placeholder="Selecciona un usuario para eliminar",
                options=options[:25],
                custom_id="user_remove_select"
            )
            select.callback = self.select_callback
            self.add_item(select)
    
    async def select_callback(self, interaction: discord.Interaction):
        user_id = int(interaction.data["values"][0])
        user = interaction.guild.get_member(user_id)
        
        if not user:
            await interaction.response.send_message(
                "No se encontró al usuario seleccionado.",
                ephemeral=True
            )
            return
        
        result = await remove_user_from_channel(self.channel, user, interaction.guild.id)
        
        if result:
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="Usuario eliminado",
                    description=f"Se han eliminado los permisos de {user.mention} en este canal.",
                    color=discord.Color.green()
                ),
                view=self.parent_view
            )
        else:
            await interaction.response.send_message(
                "Ocurrió un error al eliminar los permisos del usuario.",
                ephemeral=True
            )
    
    @ui.button(label="Volver", style=discord.ButtonStyle.secondary)
    async def back_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="Gestión de permisos de usuarios",
                description="Selecciona una acción para gestionar los permisos de usuarios.",
                color=discord.Color.blue()
            ),
            view=self.parent_view
        )

class PermissionLevelView(ui.View):
    def __init__(self, bot, channel, channel_data, parent_view, selected_user):
        super().__init__(timeout=300)
        self.bot = bot
        self.channel = channel
        self.channel_data = channel_data
        self.parent_view = parent_view
        self.selected_user = selected_user
    
    @ui.button(label="👁️ Espectador", style=discord.ButtonStyle.secondary)
    async def viewer_perm(self, interaction: discord.Interaction, button: ui.Button):
        result = await add_user_to_channel(self.channel, self.selected_user, interaction.guild.id, "viewer")
        
        if result:
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="Permisos actualizados",
                    description=f"Se han otorgado permisos de espectador a {self.selected_user.mention}.",
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
        result = await add_user_to_channel(self.channel, self.selected_user, interaction.guild.id, "moderator")
        
        if result:
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="Permisos actualizados",
                    description=f"Se han otorgado permisos de moderador a {self.selected_user.mention}.",
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
        result = await add_user_to_channel(self.channel, self.selected_user, interaction.guild.id, "co-owner")
        
        if result:
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="Permisos actualizados",
                    description=f"Se han otorgado permisos de propietario adjunto a {self.selected_user.mention}.",
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
                title="Gestión de permisos de usuarios",
                description="Selecciona una acción para gestionar los permisos de usuarios.",
                color=discord.Color.blue()
            ),
            view=self.parent_view
        )