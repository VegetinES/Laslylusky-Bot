import discord
from discord import ui
from ..database import get_voice_channels, save_voice_channel
from .channel_utils import check_manage_permission
from .channel_message import create_channel_control_message

async def handle_allow_users(interaction):
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
            "❌ No tienes permiso para añadir usuarios permitidos.",
            ephemeral=True
        )
        return
    
    view = ui.View(timeout=60)
    user_select = ui.UserSelect(
        placeholder="Selecciona usuarios para permitir",
        min_values=1,
        max_values=10
    )
    
    async def user_select_callback(select_interaction):
        selected_users = select_interaction.data["values"]
        
        if "allowed_users" not in channel_data:
            channel_data["allowed_users"] = []
        
        users_added = []
        for user_id in selected_users:
            user_id = int(user_id)
            member = interaction.guild.get_member(user_id)
            
            if member and user_id not in channel_data["allowed_users"]:
                channel_data["allowed_users"].append(user_id)
                users_added.append(member)
                
                await channel.set_permissions(
                    member,
                    connect=True,
                    view_channel=True
                )
        
        save_voice_channel(interaction.guild.id, channel.id, channel_data)
        
        await create_channel_control_message(channel, update=True)
        
        if users_added:
            mentions = ", ".join([user.mention for user in users_added])
            await select_interaction.response.send_message(
                f"✅ Se ha permitido el acceso a: {mentions}",
                ephemeral=True
            )
        else:
            await select_interaction.response.send_message(
                "❌ No se ha añadido ningún usuario nuevo.",
                ephemeral=True
            )
    
    user_select.callback = user_select_callback
    view.add_item(user_select)
    
    await interaction.response.send_message(
        "Selecciona los usuarios a los que quieres permitir el acceso:",
        view=view,
        ephemeral=True
    )

async def handle_disallow_users(interaction):
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
            "❌ No tienes permiso para gestionar usuarios permitidos.",
            ephemeral=True
        )
        return
    
    allowed_users = channel_data.get("allowed_users", [])
    if not allowed_users:
        await interaction.response.send_message(
            "❌ No hay usuarios con permisos especiales en este canal.",
            ephemeral=True
        )
        return
    
    options = []
    for user_id in allowed_users:
        member = interaction.guild.get_member(user_id)
        if member:
            options.append(
                discord.SelectOption(
                    label=member.display_name,
                    description=f"ID: {member.id}",
                    value=str(member.id)
                )
            )
    
    if not options:
        await interaction.response.send_message(
            "❌ No se encontraron usuarios con permisos especiales.",
            ephemeral=True
        )
        return
    
    view = ui.View(timeout=60)
    select = ui.Select(
        placeholder="Selecciona usuarios para quitar permisos",
        options=options[:25],
        min_values=1,
        max_values=min(len(options), 25)
    )
    
    async def select_callback(select_interaction):
        selected_users = select_interaction.data["values"]
        
        removed_users = []
        for user_id in selected_users:
            user_id = int(user_id)
            member = interaction.guild.get_member(user_id)
            
            if member and user_id in channel_data["allowed_users"]:
                channel_data["allowed_users"].remove(user_id)
                removed_users.append(member)
                
                if "managers" in channel_data and user_id in channel_data["managers"]:
                    channel_data["managers"].remove(user_id)
                
                await channel.set_permissions(member, overwrite=None)
        
        save_voice_channel(interaction.guild.id, channel.id, channel_data)
        
        await create_channel_control_message(channel, update=True)
        
        if removed_users:
            mentions = ", ".join([user.mention for user in removed_users])
            await select_interaction.response.send_message(
                f"✅ Se han quitado los permisos a: {mentions}",
                ephemeral=True
            )
        else:
            await select_interaction.response.send_message(
                "❌ No se ha quitado ningún permiso.",
                ephemeral=True
            )
    
    select.callback = select_callback
    view.add_item(select)
    
    await interaction.response.send_message(
        "Selecciona los usuarios a los que quieres quitar permisos:",
        view=view,
        ephemeral=True
    )