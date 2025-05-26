import discord
from discord import ui
from ..database import get_voice_channels, save_voice_channel
from .channel_utils import check_manage_permission, get_visibility_text
from .channel_message import create_channel_control_message

async def handle_visibility_change(interaction):
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
            "❌ No tienes permiso para cambiar la visibilidad del canal.",
            ephemeral=True
        )
        return
    
    select = ui.Select(
        placeholder="Selecciona la visibilidad",
        options=[
            discord.SelectOption(
                label="Visible", 
                description="Todos pueden ver el canal", 
                value="visible",
                emoji="👁️",
                default=channel_data.get("visibility") == "visible"
            ),
            discord.SelectOption(
                label="Oculto", 
                description="Solo visible para usuarios permitidos", 
                value="hidden",
                emoji="🔍",
                default=channel_data.get("visibility") == "hidden"
            )
        ],
        custom_id="visibility_select"
    )
    
    view = ui.View(timeout=60)
    
    async def visibility_callback(select_interaction):
        visibility = select_interaction.data["values"][0]
        
        channel_data["visibility"] = visibility
        save_voice_channel(interaction.guild.id, channel.id, channel_data)
        
        if visibility == "visible":
            await channel.set_permissions(
                interaction.guild.default_role,
                view_channel=True
            )
        elif visibility == "hidden":
            await channel.set_permissions(
                interaction.guild.default_role,
                view_channel=False
            )
            
            allowed_users = channel_data.get("allowed_users", [])
            for user_id in allowed_users:
                member = interaction.guild.get_member(user_id)
                if member:
                    await channel.set_permissions(
                        member,
                        view_channel=True
                    )
        
        await create_channel_control_message(channel, update=True)
        
        await select_interaction.response.send_message(
            f"✅ Visibilidad cambiada a: {get_visibility_text(visibility)}",
            ephemeral=True
        )
    
    select.callback = visibility_callback
    view.add_item(select)
    
    await interaction.response.send_message(
        "Selecciona la visibilidad para el canal:",
        view=view,
        ephemeral=True
    )