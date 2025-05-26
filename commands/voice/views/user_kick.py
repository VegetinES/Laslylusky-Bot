import discord
from discord import ui
from ..database import get_voice_channels, save_voice_channel
from .channel_utils import check_manage_permission

async def handle_kick_users(interaction):
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
            "❌ No tienes permiso para expulsar usuarios.",
            ephemeral=True
        )
        return
    
    if not channel.members or len(channel.members) <= 1:
        await interaction.response.send_message(
            "❌ No hay usuarios para expulsar del canal.",
            ephemeral=True
        )
        return
    
    options = []
    for member in channel.members:
        if member.id != channel_data.get("owner_id") and member.id != interaction.user.id:
            options.append(
                discord.SelectOption(
                    label=member.display_name,
                    description=f"ID: {member.id}",
                    value=str(member.id)
                )
            )
    
    if not options:
        await interaction.response.send_message(
            "❌ No hay usuarios que puedas expulsar.",
            ephemeral=True
        )
        return
    
    view = ui.View(timeout=60)
    select = ui.Select(
        placeholder="Selecciona usuarios para expulsar",
        options=options[:25],
        min_values=1,
        max_values=min(len(options), 25)
    )
    
    async def select_callback(select_interaction):
        selected_users = select_interaction.data["values"]
        
        kicked_users = []
        for user_id in selected_users:
            member = interaction.guild.get_member(int(user_id))
            if member and member in channel.members:
                try:
                    if interaction.guild.afk_channel:
                        await member.move_to(interaction.guild.afk_channel)
                    else:
                        await member.move_to(None)
                    
                    kicked_users.append(member)
                    
                    if "allowed_users" in channel_data and int(user_id) in channel_data["allowed_users"]:
                        channel_data["allowed_users"].remove(int(user_id))
                    
                    await channel.set_permissions(member, overwrite=None)
                    
                except discord.HTTPException:
                    pass
        
        save_voice_channel(interaction.guild.id, channel.id, channel_data)
        
        if kicked_users:
            mentions = ", ".join([user.mention for user in kicked_users])
            await select_interaction.response.send_message(
                f"✅ Usuarios expulsados: {mentions}",
                ephemeral=True
            )
        else:
            await select_interaction.response.send_message(
                "❌ No se pudo expulsar a ningún usuario.",
                ephemeral=True
            )
    
    select.callback = select_callback
    view.add_item(select)
    
    await interaction.response.send_message(
        "Selecciona los usuarios que quieres expulsar del canal:",
        view=view,
        ephemeral=True
    )