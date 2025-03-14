import discord
from database.get import get_server_data
from database.update import update_server_data

class ConfirmDeleteView(discord.ui.View):
    def __init__(self, guild_id, channel_id, channel):
        super().__init__(timeout=60)
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.channel = channel

    @discord.ui.button(label="Confirmar Eliminación", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            server_data = get_server_data(self.guild_id)
            
            if not server_data or "tickets" not in server_data or self.channel_id not in server_data["tickets"]:
                await interaction.response.send_message(
                    "La configuración ya ha sido eliminada o no existe.",
                    ephemeral=True
                )
                return

            channel = interaction.guild.get_channel(int(self.channel_id))
            if channel:
                try:
                    found_button = False
                    async for message in channel.history(limit=50):
                        if message.author.id == interaction.client.user.id and message.components:
                            for row in message.components:
                                for component in row.children:
                                    if isinstance(component, discord.Button) and component.custom_id.startswith("open_ticket"):
                                        await message.delete()
                                        found_button = True
                                        break
                                if found_button:
                                    break
                            if found_button:
                                break
                except Exception as e:
                    print(f"Error al buscar o eliminar mensaje con botón: {e}")

            server_data_copy = server_data.copy()

            server_data_copy["tickets"][self.channel_id]["_removed"] = True

            update_server_data(self.guild_id, "tickets", server_data_copy["tickets"])

            for child in self.children:
                child.disabled = True
                
            await interaction.response.edit_message(
                content=f"<:Si:825734135116070962> Configuración de tickets para el canal {self.channel.mention} eliminada correctamente.",
                view=self
            )
        
        except Exception as e:
            print(f"Error al eliminar configuración: {e}")
            await interaction.response.send_message(
                f"<:No:825734196256440340> Ocurrió un error: {str(e)}",
                ephemeral=True
            )

    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        for child in self.children:
            child.disabled = True
            
        await interaction.response.edit_message(
            content="<:No:825734196256440340> Eliminación cancelada.",
            view=self
        )
        
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True

async def show_tickets_modify(
    interaction: discord.Interaction,
    canal: str,
    accion: str
):
    try:
        server_data = get_server_data(interaction.guild.id)
        if not server_data or "tickets" not in server_data or canal not in server_data["tickets"]:
            await interaction.response.send_message(
                "No hay configuración de tickets para este canal.",
                ephemeral=True
            )
            return

        try:
            channel_id = int(canal)
            channel = interaction.guild.get_channel(channel_id)
            if not channel:
                await interaction.response.send_message(
                    "No se pudo encontrar el canal configurado.",
                    ephemeral=True
                )
                return
        except ValueError:
            await interaction.response.send_message(
                "ID de canal inválido.",
                ephemeral=True
            )
            return

        if accion == "restablecer":
            log_channel = server_data["tickets"][canal].get("log-channel")
            tickets_name = server_data["tickets"][canal].get("tickets-name")
            ticket_id = server_data["tickets"][canal].get("id", 1)

            server_data["tickets"][canal] = {
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
                "tickets-name": tickets_name,
                "id": ticket_id,
                "log-channel": log_channel,
                "ticket-abierto": {
                    "activado": False,
                    "title": "Ticket Abierto",
                    "descripcion": "Tu ticket ha sido abierto. Un miembro del staff se pondrá en contacto contigo pronto.",
                    "imagen": None,
                    "color": None,
                    "footer": None,
                    "mensaje": None
                },
                "ticket-abrir": server_data["tickets"][canal].get("ticket-abrir", False),
                "setup_stage": 1
            }

            if "_removed" in server_data["tickets"][canal]:
                del server_data["tickets"][canal]["_removed"]
            
            if update_server_data(interaction.guild.id, "tickets", server_data["tickets"]):
                await interaction.response.send_message(
                    f"<:Si:825734135116070962> Configuración de tickets para el canal {channel.mention} restablecida.\n\n"
                    f"- Se han restablecido los permisos\n"
                    f"- Se ha restablecido el mensaje de ticket abierto\n\n"
                    f"⚠️ **Paso obligatorio siguiente**: Configura los permisos con el comando:\n"
                    f"`/config tickets permisos canal:{canal} permiso:Gestionar tickets accion:añadir roles:<roles o usuarios>`",
                    ephemeral=False
                )
            else:
                await interaction.response.send_message(
                    "<:No:825734196256440340> Ocurrió un error al restablecer la configuración.",
                    ephemeral=True
                )
                
        elif accion == "eliminar":
            view = ConfirmDeleteView(interaction.guild.id, canal, channel)
            await interaction.response.send_message(
                f"⚠️ **Confirmación requerida:** ¿Estás seguro de eliminar la configuración de tickets para el canal {channel.mention}?\n\n"
                "Esta acción no se puede deshacer y eliminará todos los datos de configuración asociados.",
                view=view,
                ephemeral=True
            )
            
        else:
            await interaction.response.send_message(
                "Acción no válida. Debe ser 'restablecer' o 'eliminar'.",
                ephemeral=True
            )

    except Exception as e:
        print(f"Error en show_tickets_modify: {e}")
        await interaction.response.send_message(
            f"<:No:825734196256440340> Ocurrió un error: {str(e)}",
            ephemeral=True
        )