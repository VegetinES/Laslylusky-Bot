import discord
from ..database import get_voice_channels, save_voice_channel
from .channel_utils import get_privacy_text, get_visibility_text

async def create_channel_control_message(channel, update=False):
    try:
        guild_id = channel.guild.id
        
        from ..database import get_voice_channels, get_voice_config
        voice_channels = get_voice_channels(guild_id)
        
        if str(channel.id) not in voice_channels:
            return False
        
        channel_data = voice_channels[str(channel.id)]
        owner_id = channel_data.get("owner_id")
        owner = channel.guild.get_member(owner_id) if owner_id else None
        
        embed = discord.Embed(
            title=f"Panel de Control: {channel.name}",
            description=(
                "Este panel te permite configurar el canal de voz.\n"
                f"👑 **Propietario:** {owner.mention if owner else 'Desconocido'}\n\n"
                "ℹ️ **Configuración actual:**\n"
                f"• **Privacidad:** {get_privacy_text(channel_data.get('privacy', 'public'))}\n"
                f"• **Visibilidad:** {get_visibility_text(channel_data.get('visibility', 'visible'))}\n"
                f"• **Límite de usuarios:** {channel.user_limit if channel.user_limit else 'Sin límite'}"
            ),
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="Opciones disponibles",
            value=(
                "• **Nombre**: Cambia el nombre del canal\n"
                "• **Privacidad**: Controla quién puede unirse\n"
                "• **Visibilidad**: Controla quién puede ver el canal\n"
                "• **Permitir**: Añade usuarios al canal\n"
                "• **Quitar**: Elimina permisos a usuarios\n"
                "• **Gestionar**: Otorga permisos de gestión\n"
                "• **Expulsar**: Expulsa usuarios del canal\n"
                "• **Límite**: Establece número máximo de usuarios\n"
            ),
            inline=False
        )

        embed.set_image(url="https://i.imgur.com/nyYjTWt.png")
        
        existing_message = None
        
        if "control_message_id" in channel_data:
            try:
                existing_message = await channel.fetch_message(channel_data["control_message_id"])
            except (discord.NotFound, discord.HTTPException):
                existing_message = None
        
        if (update and not existing_message) or not update:
            async for message in channel.history(limit=10):
                if message.author.id == channel.guild.me.id and message.embeds and len(message.embeds) > 0:
                    if message.embeds[0].title and "Panel de Control" in message.embeds[0].title:
                        existing_message = message
                        break
        
        from .channel_view import ChannelControlView
        view = ChannelControlView(owner_id)
        
        if existing_message:
            try:
                await existing_message.edit(embed=embed, view=view)
                message = existing_message
            except discord.HTTPException:
                message = await channel.send(embed=embed, view=view)
        else:
            message = await channel.send(embed=embed, view=view)
            
            try:
                await message.pin()
            except discord.HTTPException:
                pass
        
        channel_data["control_message_id"] = message.id
        save_voice_channel(guild_id, channel.id, channel_data)
        
        return True
    except Exception as e:
        print(f"Error al crear mensaje de control: {e}")
        return False