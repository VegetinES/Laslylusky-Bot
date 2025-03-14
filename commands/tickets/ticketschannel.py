import discord
from database.get import get_server_data
from database.update import update_server_data
import re

async def show_tickets_channel(interaction: discord.Interaction, channel: discord.TextChannel, canal_logs: discord.TextChannel, ticket_name: str):
    try:
        if len(ticket_name) > 15:
            await interaction.response.send_message(
                "El nombre del ticket no puede tener más de 15 caracteres.",
                ephemeral=True
            )
            return

        if not re.match(r'^[a-zA-Z0-9\s\-_áéíóúÁÉÍÓÚñÑ{}\[\]()]+$', ticket_name):
            await interaction.response.send_message(
                "El nombre del ticket contiene caracteres no válidos. Solo se permiten letras, números, espacios, guiones, guiones bajos y los caracteres {}, [], ().",
                ephemeral=True
            )
            return

        if "{id}" not in ticket_name:
            await interaction.response.send_message(
                "El nombre del ticket debe contener {id} para la numeración automática.",
                ephemeral=True
            )
            return

        server_data = get_server_data(interaction.guild.id)
        if not server_data:
            await interaction.response.send_message(
                "No hay datos configurados para este servidor. Usa el comando `/config update` primero.",
                ephemeral=True
            )
            return

        if "tickets" not in server_data:
            server_data["tickets"] = {}
        
        channel_id = str(channel.id)

        base_ticket_config = {
            "perms": {
                "manage-roles": [0],
                "manage-users": [0],
                "see-roles": [0],
                "see-users": [0],
                "close-roles": [0],
                "close-users": [0],
                "add-del-usr-roles": [0],
                "add-del-usr-users": [0]
            },
            "tickets-name": ticket_name,
            "id": 1,
            "log-channel": canal_logs.id,
            "setup_stage": 1,
            "ticket-abierto": {
                "activado": False,
                "title": "Ticket Abierto",
                "descripcion": "Tu ticket ha sido abierto. Un miembro del staff se pondrá en contacto contigo pronto.",
                "imagen": None,
                "color": None,
                "footer": None,
                "mensaje": None
            },
            "ticket-abrir": False
        }

        if channel_id in server_data["tickets"]:
            if server_data["tickets"][channel_id].get("_removed") or True:
                if server_data["tickets"][channel_id].get("_removed"):
                    del server_data["tickets"][channel_id]["_removed"]

                server_data["tickets"][channel_id] = base_ticket_config
            else:
                server_data["tickets"][channel_id]["tickets-name"] = ticket_name
                server_data["tickets"][channel_id]["log-channel"] = canal_logs.id
        else:
            server_data["tickets"][channel_id] = base_ticket_config

        if update_server_data(interaction.guild.id, "tickets", server_data["tickets"]):
            await interaction.response.send_message(
                f"<:Si:825734135116070962> Canal de tickets configurado correctamente.\n"
                f"Canal: {channel.mention}\n"
                f"Canal de logs: {canal_logs.mention}\n"
                f"Nombre de ticket: `{ticket_name}`\n\n"
                f"⚠️ **Paso obligatorio siguiente**: Configura los permisos con el comando:\n"
                f"`/config tickets permisos canal:{channel_id} permiso:Gestionar tickets accion:añadir roles:<roles o usuarios>`\n\n"
                f"Es necesario configurar al menos un rol o usuario con permisos de gestión.",
                ephemeral=False
            )
        else:
            await interaction.response.send_message(
                "<:No:825734196256440340> Ocurrió un error al guardar la configuración.",
                ephemeral=True
            )

    except Exception as e:
        print(f"Error en show_tickets_channel: {e}")
        await interaction.response.send_message(
            f"<:No:825734196256440340> Ocurrió un error: {str(e)}",
            ephemeral=True
        )