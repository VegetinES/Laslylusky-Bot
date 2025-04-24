import discord
from datetime import datetime
from .....tickets.constants import COLORS

async def create_ticket_messages_embed(channel_id, ticket_config, interaction):
    embed = discord.Embed(
        title="Mensajes de tickets",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    
    channel = interaction.guild.get_channel(int(channel_id))
    
    embed.add_field(
        name="Canal de tickets",
        value=f"{channel.mention if channel else f'`Canal ID: {channel_id}`'}",
        inline=False
    )
    
    open_message = ticket_config.get("open_message", {})
    
    if open_message:
        is_embed = open_message.get("embed", False)
        color_name = open_message.get("color", "default")
        color_info = COLORS.get(color_name, ["Azul"])[1] if color_name in COLORS else "Azul"
        
        embed.add_field(
            name="Mensaje para abrir tickets",
            value=(
                f"**Tipo:** {'Embed' if is_embed else 'Texto normal'}\n"
                f"**Título:** {open_message.get('title', 'No configurado') if is_embed else 'N/A'}\n"
                f"**Descripción:** {(open_message.get('description', '')[:100] + '...' if len(open_message.get('description', '')) > 100 else open_message.get('description', 'No configurado')) if is_embed else 'N/A'}\n"
                f"**Color:** {color_info if is_embed else 'N/A'}\n"
                f"**Texto normal:** {(open_message.get('plain_message', '')[:100] + '...' if len(open_message.get('plain_message', '')) > 100 else open_message.get('plain_message', 'No configurado')) if open_message.get('plain_message') else 'No configurado'}"
            ),
            inline=False
        )
    else:
        embed.add_field(
            name="Mensaje para abrir tickets",
            value="No configurado",
            inline=False
        )
    
    opened_messages = ticket_config.get("opened_messages", {})
    
    if opened_messages and isinstance(opened_messages, dict):
        for button_id, msg_config in opened_messages.items():
            is_embed = msg_config.get("embed", False)
            color_name = msg_config.get("color", "default")
            color_info = COLORS.get(color_name, ["Azul"])[1] if color_name in COLORS else "Azul"
            
            embed.add_field(
                name=f"Mensaje para tickets abiertos con botón '{button_id}'",
                value=(
                    f"**Tipo:** {'Embed' if is_embed else 'Texto normal'}\n"
                    f"**Título:** {msg_config.get('title', 'No configurado') if is_embed else 'N/A'}\n"
                    f"**Descripción:** {(msg_config.get('description', '')[:100] + '...' if len(msg_config.get('description', '')) > 100 else msg_config.get('description', 'No configurado')) if is_embed else 'N/A'}\n"
                    f"**Color:** {color_info if is_embed else 'N/A'}\n"
                    f"**Texto normal:** {(msg_config.get('plain_message', '')[:100] + '...' if len(msg_config.get('plain_message', '')) > 100 else msg_config.get('plain_message', 'No configurado')) if msg_config.get('plain_message') else 'No configurado'}"
                ),
                inline=False
            )
    else:
        embed.add_field(
            name="Mensajes para tickets abiertos",
            value="No configurados",
            inline=False
        )
    
    embed.set_footer(text=f"Solicitado por {interaction.user.name}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
    return embed