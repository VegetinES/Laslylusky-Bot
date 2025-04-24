import discord
from datetime import datetime

async def create_ticket_detail_embed(channel_id, ticket_config, interaction):
    embed = discord.Embed(
        title="Detalles de configuración de tickets",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    
    channel = interaction.guild.get_channel(int(channel_id))
    
    log_channel_id = ticket_config.get("log_channel")
    log_channel = interaction.guild.get_channel(int(log_channel_id)) if log_channel_id else None

    counter_info = ""
    auto_increment = ticket_config.get("auto_increment", {})
    if auto_increment and isinstance(auto_increment, dict):
        counter_info = "\n".join([f"• {key}: {value}" for key, value in auto_increment.items()])
    if not counter_info:
        counter_info = "No hay contadores configurados"
    
    embed.add_field(
        name="Información general",
        value=(
            f"🎫 **Canal:** {channel.mention if channel else f'`Canal ID: {channel_id}`'}\n"
            f"📋 **Canal de logs:** {log_channel.mention if log_channel else 'No configurado'}\n"
            f"🔢 **Contadores automáticos:**\n{counter_info}\n"
        ),
        inline=False
    )

    open_message = ticket_config.get("open_message", {})
    buttons = open_message.get("buttons", [])
    
    if buttons:
        buttons_info = "\n".join([
            f"• **{btn.get('label', 'Desconocido')}** (`{btn.get('id', 'default')}`) - Formato: `{btn.get('name_format', 'ticket-{id}')}`"
            for btn in buttons
        ])
        embed.add_field(
            name="Botones configurados",
            value=buttons_info or "No hay botones configurados",
            inline=False
        )
    else:
        embed.add_field(
            name="Botones configurados",
            value="No hay botones configurados",
            inline=False
        )

    embed.set_footer(text=f"Solicitado por {interaction.user.name}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
    return embed