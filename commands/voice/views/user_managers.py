import discord
from discord import ui
from ..database import get_voice_channels, save_voice_channel
from .channel_utils import check_manage_permission

async def handle_manage_permissions(interaction):
    channel = interaction.channel
    voice_channels = get_voice_channels(interaction.guild.id)
    
    if str(channel.id) not in voice_channels:
        await interaction.response.send_message(
            "❌ Este canal no es un canal de voz personalizado.",
            ephemeral=True
        )
        return
    
    channel_data = voice_channels[str(channel.id)]
    
    if interaction.user.id != channel_data.get("owner_id"):
        await interaction.response.send_message(
            "❌ Solo el propietario del canal puede gestionar permisos.",
            ephemeral=True
        )
        return
    
    view = ui.View(timeout=60)
    
    add_btn = ui.Button(
        label="Añadir gestores",
        style=discord.ButtonStyle.success,
        custom_id="add_managers"
    )
    
    async def add_managers_callback(btn_interaction):
        add_view = ui.View(timeout=60)
        user_select = ui.UserSelect(
            placeholder="Selecciona usuarios para añadir como gestores",
            min_values=1,
            max_values=10
        )
        
        async def user_select_callback(select_interaction):
            selected_users = select_interaction.data["values"]
            
            if "managers" not in channel_data:
                channel_data["managers"] = []
            
            users_added = []
            for user_id in selected_users:
                user_id = int(user_id)
                member = interaction.guild.get_member(user_id)
                
                if member and user_id not in channel_data["managers"]:
                    channel_data["managers"].append(user_id)
                    
                    if "allowed_users" not in channel_data:
                        channel_data["allowed_users"] = []
                    if user_id not in channel_data["allowed_users"]:
                        channel_data["allowed_users"].append(user_id)
                    
                    users_added.append(member)
                    
                    await channel.set_permissions(
                        member,
                        connect=True,
                        view_channel=True,
                        manage_channels=True,
                        move_members=True,
                        mute_members=True,
                        deafen_members=True
                    )
            
            save_voice_channel(interaction.guild.id, channel.id, channel_data)
            
            if users_added:
                mentions = ", ".join([user.mention for user in users_added])
                await select_interaction.response.send_message(
                    f"✅ Se han otorgado permisos de gestión a: {mentions}",
                    ephemeral=True
                )
            else:
                await select_interaction.response.send_message(
                    "❌ No se ha añadido ningún gestor nuevo.",
                    ephemeral=True
                )
        
        user_select.callback = user_select_callback
        add_view.add_item(user_select)
        
        await btn_interaction.response.edit_message(
            content="Selecciona los usuarios para añadir como gestores:",
            view=add_view
        )
    
    add_btn.callback = add_managers_callback
    view.add_item(add_btn)
    
    if "managers" in channel_data and channel_data["managers"]:
        remove_btn = ui.Button(
            label="Quitar gestores",
            style=discord.ButtonStyle.danger,
            custom_id="remove_managers"
        )
        
        async def remove_managers_callback(btn_interaction):
            await handle_remove_managers(btn_interaction, interaction, channel_data, channel)
        
        remove_btn.callback = remove_managers_callback
        view.add_item(remove_btn)
    
    back_btn = ui.Button(
        label="Volver",
        style=discord.ButtonStyle.secondary,
        custom_id="back_to_main"
    )
    
    async def back_callback(btn_interaction):
        await btn_interaction.response.send_message(
            "Operación cancelada",
            ephemeral=True
        )
    
    back_btn.callback = back_callback
    view.add_item(back_btn)
    
    await interaction.response.send_message(
        "Selecciona una acción para gestionar permisos:",
        view=view,
        ephemeral=True
    )

async def handle_remove_managers(btn_interaction, interaction, channel_data, channel):
    options = []
    for user_id in channel_data["managers"]:
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
        await btn_interaction.response.send_message(
            "❌ No hay gestores disponibles para quitar.",
            ephemeral=True
        )
        return
    
    remove_view = ui.View(timeout=60)
    select = ui.Select(
        placeholder="Selecciona gestores para quitar",
        options=options,
        min_values=1,
        max_values=min(len(options), 25)
    )
    
    async def remove_select_callback(select_interaction):
        selected_users = select_interaction.data["values"]
        
        removed_users = []
        for user_id in selected_users:
            user_id = int(user_id)
            member = interaction.guild.get_member(user_id)
            
            if member and user_id in channel_data["managers"]:
                channel_data["managers"].remove(user_id)
                removed_users.append(member)
                
                await channel.set_permissions(
                    member,
                    connect=True,
                    view_channel=True,
                    manage_channels=False,
                    move_members=False,
                    mute_members=False,
                    deafen_members=False
                )
        
        save_voice_channel(interaction.guild.id, channel.id, channel_data)
        
        if removed_users:
            mentions = ", ".join([user.mention for user in removed_users])
            await select_interaction.response.send_message(
                f"✅ Se han quitado permisos de gestión a: {mentions}",
                ephemeral=True
            )
        else:
            await select_interaction.response.send_message(
                "❌ No se ha quitado ningún gestor.",
                ephemeral=True
            )
    
    select.callback = remove_select_callback
    remove_view.add_item(select)
    
    await btn_interaction.response.edit_message(
        content="Selecciona los gestores a los que quieres quitar permisos:",
        view=remove_view
    )