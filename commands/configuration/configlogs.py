# configlogs.py
import discord
from discord.ext import commands
from database.get import get_specific_field
from database.update import update_server_data

from .configlogs_constants import LOG_TYPES
from .configlogs_models import LogMessageModel
from .configlogs_views import LogConfigView
from .configlogs_preview import create_preview

async def show_config_logs(interaction: discord.Interaction, tipo: str):
    try:
        guild_id = interaction.guild.id
        
        if tipo not in LOG_TYPES:
            options = "\n".join([f"• `{log_type}` - {LOG_TYPES[log_type]['name']}" for log_type in LOG_TYPES])
            await interaction.response.send_message(
                f"<:No:825734196256440340> Tipo de log no válido. Opciones disponibles:\n{options}",
                ephemeral=True
            )
            return

        guild_data = get_specific_field(guild_id, "audit_logs")
        if not guild_data:
            await interaction.response.send_message(
                "<:No:825734196256440340> No hay configuración de logs para este servidor. Usa el comando `/config update` primero.",
                ephemeral=True
            )
            return
        
        if tipo not in guild_data:
            guild_data[tipo] = {
                "activated": False,
                "log_channel": 0,
                "message": LogMessageModel.create_default()
            }
            
            update_server_data(guild_id, "audit_logs", guild_data)
        
        if f"{tipo}_messages" in guild_data[tipo]:
            legacy_message = guild_data[tipo].get(f"{tipo}_messages", "")
            guild_data[tipo]["message"] = LogMessageModel.from_legacy_format(legacy_message)

            if f"{tipo}_messages" in guild_data[tipo]:
                del guild_data[tipo][f"{tipo}_messages"]

            update_server_data(guild_id, f"audit_logs/{tipo}", guild_data[tipo])

        if "message" not in guild_data[tipo] or not isinstance(guild_data[tipo]["message"], dict):
            guild_data[tipo]["message"] = LogMessageModel.create_default()
            update_server_data(guild_id, f"audit_logs/{tipo}", guild_data[tipo])
        
        message_data = guild_data[tipo]["message"]
        if "image" not in message_data or not isinstance(message_data["image"], dict):
            message_data["image"] = {"has": False, "param": ""}
        if "thumbnail" not in message_data or not isinstance(message_data["thumbnail"], dict):
            message_data["thumbnail"] = {"has": False, "param": ""}
        if "fields" not in message_data or not isinstance(message_data["fields"], dict):
            existing_fields = message_data.get("fields", {})
            if isinstance(existing_fields, dict):
                message_data["fields"] = existing_fields
            else:
                message_data["fields"] = {}
        if "color" not in message_data or not message_data["color"]:
            message_data["color"] = "default"
        
        if "message" in guild_data[tipo]:
            current_fields = guild_data[tipo]["message"].get("fields", {})
            if current_fields:
                message_data["fields"] = current_fields
            
        update_server_data(guild_id, f"audit_logs/{tipo}/message", message_data)

        config_data = guild_data[tipo]
        is_activated = config_data.get("activated", False)
        channel_id = config_data.get("log_channel", 0)
        channel = interaction.guild.get_channel(channel_id) if channel_id else None

        view = LogConfigView(interaction, guild_id, tipo, config_data)

        preview_data = await create_preview(tipo, message_data, interaction.guild)
        
        if is_activated:
            await interaction.response.send_message(
                content=f"{preview_data['content']}",
                embed=preview_data.get("embed"),
                view=view
            )
        else:
            if channel and message_data:
                content = f"Los **{LOG_TYPES[tipo]['name']}** están desactivados actualmente.\n"
                content += f"Canal configurado: {channel.mention}\n"
                content += f"Tipo: {'Embed' if message_data.get('embed', False) else 'Mensaje normal'}"
                
                await interaction.response.send_message(content=content, view=view)
            else:
                await interaction.response.send_message(
                    content=f"Los **{LOG_TYPES[tipo]['name']}** están desactivados y no están completamente configurados.",
                    view=view
                )
        
    except Exception as e:
        print(f"Error en show_config_logs: {e}")
        await interaction.response.send_message(
            f"<:No:825734196256440340> Ocurrió un error: {str(e)}",
            ephemeral=True
        )