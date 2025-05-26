import discord
from discord import ui
from ..permissions import add_user_to_channel, remove_user_from_channel, add_role_to_channel
from ..utils import get_permission_description

class PermissionView(ui.View):
    def __init__(self, bot, channel, channel_data, parent_view):
        super().__init__(timeout=300)
        self.bot = bot
        self.channel = channel
        self.channel_data = channel_data
        self.parent_view = parent_view
    
    @ui.button(label="Gestionar usuarios", style=discord.ButtonStyle.primary)
    async def manage_users(self, interaction: discord.Interaction, button: ui.Button):
        from .user_permission_view import UserPermissionView
        view = UserPermissionView(self.bot, self.channel, self.channel_data, self)
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="Gestión de permisos de usuarios",
                description="Selecciona una acción para gestionar los permisos de usuarios.",
                color=discord.Color.blue()
            ),
            view=view
        )
    
    @ui.button(label="Gestionar roles", style=discord.ButtonStyle.primary)
    async def manage_roles(self, interaction: discord.Interaction, button: ui.Button):
        from .role_permission_view import RolePermissionView
        view = RolePermissionView(self.bot, self.channel, self.channel_data, self)
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="Gestión de permisos de roles",
                description="Selecciona una acción para gestionar los permisos de roles.",
                color=discord.Color.blue()
            ),
            view=view
        )
    
    @ui.button(label="Volver", style=discord.ButtonStyle.secondary)
    async def back_button(self, interaction: discord.Interaction, button: ui.Button):
        from ..utils import get_channel_info_embed
        embed = get_channel_info_embed(self.channel, self.channel_data)
        await interaction.response.edit_message(
            embed=embed,
            view=self.parent_view
        )