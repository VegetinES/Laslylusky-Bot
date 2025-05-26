import discord
from discord import ui
from ..database import get_voice_config, get_voice_channels, save_voice_channel

def get_privacy_text(privacy):
    if privacy == "public":
        return "Público (todos pueden unirse)"
    elif privacy == "locked":
        return "Bloqueado (nadie puede unirse)"
    elif privacy == "private":
        return "Privado (solo usuarios permitidos)"
    return "Desconocido"

def get_visibility_text(visibility):
    if visibility == "visible":
        return "Visible (todos pueden ver)"
    elif visibility == "hidden":
        return "Oculto (solo visibles para usuarios permitidos)"
    return "Desconocido"

async def check_manage_permission(interaction, channel_data):
    if interaction.user.id == channel_data.get("owner_id"):
        return True
    
    if "managers" in channel_data and interaction.user.id in channel_data["managers"]:
        return True
    
    config = get_voice_config(interaction.guild.id)
    admin_roles = config.get("admin_roles", [])
    
    for role in interaction.user.roles:
        if role.id in admin_roles:
            return True
    
    if interaction.user.guild_permissions.administrator:
        return True
    
    return False