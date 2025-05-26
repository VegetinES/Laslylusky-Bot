import discord
from discord import ui
from ..database import get_voice_channels, save_voice_channel
from .channel_utils import check_manage_permission, get_privacy_text, get_visibility_text
from .channel_modals import ChannelNameModal, ChannelLimitModal
from .channel_message import create_channel_control_message

class ChannelControlView(ui.View):
    def __init__(self, owner_id):
        super().__init__(timeout=None)
        self.owner_id = owner_id
    
    @ui.button(emoji="<:changename:1372867073151340604>", style=discord.ButtonStyle.secondary, custom_id="voice:name", row=0)
    async def change_name(self, interaction: discord.Interaction, button: ui.Button):
        channel = interaction.channel
        voice_channels = get_voice_channels(interaction.guild.id)
        
        if str(channel.id) not in voice_channels:
            await interaction.response.send_message(
                "❌ Este canal no es un canal de voz personalizado.",
                ephemeral=True
            )
            return
        
        channel_data = voice_channels[str(channel.id)]
        
        if not await check_manage_permission(interaction, channel_data):
            await interaction.response.send_message(
                "❌ No tienes permiso para cambiar el nombre del canal.",
                ephemeral=True
            )
            return
        
        modal = ChannelNameModal(channel)
        await interaction.response.send_modal(modal)
    
    @ui.button(emoji="<:privacy:1372859433532526622>", style=discord.ButtonStyle.secondary, custom_id="voice:privacy", row=0)
    async def change_privacy(self, interaction: discord.Interaction, button: ui.Button):
        from .privacy_view import handle_privacy_change
        await handle_privacy_change(interaction)
    
    @ui.button(emoji="<:hidden:1372865876411416616>", style=discord.ButtonStyle.secondary, custom_id="voice:visibility", row=0)
    async def change_visibility(self, interaction: discord.Interaction, button: ui.Button):
        from .visibility_view import handle_visibility_change
        await handle_visibility_change(interaction)
    
    @ui.button(emoji="<:adduser:1372865348684222514>", style=discord.ButtonStyle.secondary, custom_id="voice:allow", row=0)
    async def allow_users(self, interaction: discord.Interaction, button: ui.Button):
        from .user_allow import handle_allow_users
        await handle_allow_users(interaction)

    @ui.button(emoji="<:removeuser:1372865334360543303>", style=discord.ButtonStyle.secondary, custom_id="voice:disallow", row=1)
    async def disallow_users(self, interaction: discord.Interaction, button: ui.Button):
        from .user_allow import handle_disallow_users
        await handle_disallow_users(interaction)
    
    @ui.button(emoji="<:manage:1372866272555175996>", style=discord.ButtonStyle.secondary, custom_id="voice:manage", row=1)
    async def manage_permissions(self, interaction: discord.Interaction, button: ui.Button):
        from .user_managers import handle_manage_permissions
        await handle_manage_permissions(interaction)
    
    @ui.button(emoji="<:kick:1372867800015568907>", style=discord.ButtonStyle.secondary, custom_id="voice:kick", row=1)
    async def kick_users(self, interaction: discord.Interaction, button: ui.Button):
        from .user_kick import handle_kick_users
        await handle_kick_users(interaction)
    
    @ui.button(emoji="<:limit:1372865358670860328>", style=discord.ButtonStyle.secondary, custom_id="voice:limit", row=1)
    async def change_limit(self, interaction: discord.Interaction, button: ui.Button):
        channel = interaction.channel
        voice_channels = get_voice_channels(interaction.guild.id)
        
        if str(channel.id) not in voice_channels:
            await interaction.response.send_message(
                "❌ Este canal no es un canal de voz personalizado.",
                ephemeral=True
            )
            return
        
        channel_data = voice_channels[str(channel.id)]
        
        if not await check_manage_permission(interaction, channel_data):
            await interaction.response.send_message(
                "❌ No tienes permiso para cambiar el límite de usuarios.",
                ephemeral=True
            )
            return
        
        modal = ChannelLimitModal(channel)
        await interaction.response.send_modal(modal)