import discord
from discord import ui
from ..database import get_voice_channels, save_voice_channel
from .channel_utils import check_manage_permission, get_privacy_text
from .channel_message import create_channel_control_message

async def handle_privacy_change(interaction):
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
            "❌ No tienes permiso para cambiar la privacidad del canal.",
            ephemeral=True
        )
        return
    
    select = ui.Select(
        placeholder="Selecciona el nivel de privacidad",
        options=[
            discord.SelectOption(
                label="Público", 
                description="Cualquiera puede unirse", 
                value="public",
                emoji="🌐",
                default=channel_data.get("privacy") == "public"
            ),
            discord.SelectOption(
                label="Bloqueado", 
                description="Nadie puede unirse", 
                value="locked",
                emoji="🔒",
                default=channel_data.get("privacy") == "locked"
            ),
            discord.SelectOption(
                label="Privado", 
                description="Solo usuarios permitidos", 
                value="private",
                emoji="🔐",
                default=channel_data.get("privacy") == "private"
            )
        ],
        custom_id="privacy_select"
    )
    
    view = ui.View(timeout=60)
    
    async def privacy_callback(select_interaction):
        try:
            privacy = select_interaction.data["values"][0]
            
            channel_data["privacy"] = privacy
            save_voice_channel(interaction.guild.id, channel.id, channel_data)
            
            if privacy == "public":
                await channel.set_permissions(
                    interaction.guild.default_role,
                    connect=True
                )
            elif privacy == "locked":
                await channel.set_permissions(
                    interaction.guild.default_role,
                    connect=False
                )
            elif privacy == "private":
                await channel.set_permissions(
                    interaction.guild.default_role,
                    connect=False
                )
                
                allowed_users = channel_data.get("allowed_users", [])
                for user_id in allowed_users:
                    member = interaction.guild.get_member(user_id)
                    if member:
                        await channel.set_permissions(
                            member,
                            connect=True,
                            view_channel=True
                        )
            
            from ..database import get_voice_config
            config = get_voice_config(interaction.guild.id)
            admin_roles = config.get("admin_roles", [])
            
            for role_id in admin_roles:
                role = interaction.guild.get_role(role_id)
                if role:
                    await channel.set_permissions(
                        role,
                        connect=True,
                        speak=True,
                        manage_channels=True,
                        move_members=True,
                        mute_members=True,
                        deafen_members=True
                    )
            
            await create_channel_control_message(channel, update=True)
            
            try:
                await select_interaction.response.send_message(
                    f"✅ Privacidad cambiada a: {get_privacy_text(privacy)}",
                    ephemeral=True
                )
            except discord.InteractionResponded:
                await select_interaction.followup.send(
                    f"✅ Privacidad cambiada a: {get_privacy_text(privacy)}",
                    ephemeral=True
                )
        except Exception as e:
            print(f"Error al cambiar privacidad: {e}")
            try:
                await select_interaction.response.send_message(
                    f"❌ Error al cambiar privacidad: {str(e)}",
                    ephemeral=True
                )
            except discord.InteractionResponded:
                await select_interaction.followup.send(
                    f"❌ Error al cambiar privacidad: {str(e)}",
                    ephemeral=True
                )
    
    select.callback = privacy_callback
    view.add_item(select)
    
    await interaction.response.send_message(
        "Selecciona el nivel de privacidad para el canal:",
        view=view,
        ephemeral=True
    )