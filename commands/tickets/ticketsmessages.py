import discord
from database.get import get_server_data
from database.update import update_server_data
from .ticketsutils import get_ticket_config_state, CONFIG_STATE, parse_color

async def show_tickets_messages(
    interaction: discord.Interaction,
    bot,
    channel_id: str,
    message_type: str,
    title: str,
    description: str,
    image: str = None,
    footer: str = None,
    color: str = None,
    mensaje: str = None
):
    try:
        config_state = get_ticket_config_state(interaction.guild.id, channel_id)
        
        if config_state < CONFIG_STATE["PERMISOS_CONFIGURADOS"]:
            await interaction.response.send_message(
                "⚠️ **Error**: Debes configurar los permisos antes de configurar los mensajes.\n\n"
                f"Usa el comando:\n`/config tickets permisos canal:{channel_id} permiso:Gestionar tickets accion:añadir roles:<roles o usuarios>`",
                ephemeral=True
            )
            return

        if len(title) > 256:
            await interaction.response.send_message(
                "El título no puede tener más de 256 caracteres.",
                ephemeral=True
            )
            return

        if len(description) > 4000:
            await interaction.response.send_message(
                "La descripción no puede tener más de 4000 caracteres.",
                ephemeral=True
            )
            return

        if footer and len(footer) > 2048:
            await interaction.response.send_message(
                "El footer no puede tener más de 2048 caracteres.",
                ephemeral=True
            )
            return
            
        if mensaje and len(mensaje) > 2000:
            await interaction.response.send_message(
                "El mensaje adicional no puede tener más de 2000 caracteres.",
                ephemeral=True
            )
            return

        if image:
            image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.webp']
            if not any(image.lower().endswith(ext) for ext in image_extensions):
                await interaction.response.send_message(
                    "La URL de la imagen debe terminar con una extensión válida: .png, .jpg, .jpeg, .gif, .webp",
                    ephemeral=True
                )
                return

        if mensaje:
            mensaje = mensaje.replace(r"{\n}", "\n")

        server_data = get_server_data(interaction.guild.id)
        if not server_data or "tickets" not in server_data or channel_id not in server_data["tickets"]:
            await interaction.response.send_message(
                "No hay configuración de tickets para este canal. Configura primero el canal con `/config tickets canal`.",
                ephemeral=True
            )
            return

        tickets_config = server_data["tickets"][channel_id]

        color_value = None
        if color:
            color_value = parse_color(color)

        embed_preview = discord.Embed(
            title=title,
            description=description,
            color=color_value if color_value is not None else discord.Color.blue()
        )
        if image:
            embed_preview.set_image(url=image)
        if footer:
            embed_preview.set_footer(text=footer)

        if message_type == "ticket-abierto":
            tickets_config["ticket-abierto"] = {
                "activado": True,
                "title": title,
                "descripcion": description,
                "imagen": image,
                "color": color_value,
                "footer": footer,
                "mensaje": mensaje
            }

            update_server_data(interaction.guild.id, f"tickets/{channel_id}", tickets_config)

            if tickets_config.get("ticket-abrir", False):
                tickets_config["setup_stage"] = 3
                update_server_data(interaction.guild.id, f"tickets/{channel_id}", tickets_config)
                
                completion_status = "<:Si:825734135116070962> Mensaje de ticket abierto configurado. **¡Configuración completada!** El sistema de tickets está listo para usarse."
            else:
                completion_status = "<:Si:825734135116070962> Mensaje de ticket abierto configurado.\n\n⚠️ **Paso final obligatorio**: Configura también el botón para abrir tickets con:\n`/config tickets mensajes canal:" + channel_id + " tipo:abrir ticket título:<título> descripción:<descripción>`"
            
            if mensaje:
                await interaction.response.send_message(
                    f"{completion_status}\n\n**Mensaje adicional:**\n{mensaje}\n\n**Embed:**",
                    embed=embed_preview,
                    ephemeral=False
                )
            else:
                await interaction.response.send_message(
                    f"{completion_status}\n\nAsí es como se verá:",
                    embed=embed_preview,
                    ephemeral=False
                )
            
        elif message_type == "abrir-ticket":
            tickets_config["ticket-abrir"] = True

            if tickets_config.get("ticket-abierto", {}).get("activado", False):
                tickets_config["setup_stage"] = 3 

            update_server_data(interaction.guild.id, f"tickets/{channel_id}", tickets_config)

            target_channel = interaction.guild.get_channel(int(channel_id))
            if not target_channel:
                await interaction.response.send_message(
                    "<:No:825734196256440340> No se pudo encontrar el canal configurado.",
                    ephemeral=True
                )
                return

            class TicketButton(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=None)
                    self.add_item(discord.ui.Button(
                        style=discord.ButtonStyle.success,
                        label="Abrir Ticket",
                        emoji="🎫",
                        custom_id=f"open_ticket:{channel_id}"
                    ))

            await interaction.response.send_message(
                "<:Si:825734135116070962> Mensaje para abrir tickets configurado. Enviando al canal...",
                ephemeral=True
            )
            
            await target_channel.send(
                embed=embed_preview,
                view=TicketButton()
            )
            
            if tickets_config.get("ticket-abierto", {}).get("activado", False):
                completion_message = "<:Si:825734135116070962> **¡Configuración completada!** El sistema de tickets está listo para usarse."
            else:
                completion_message = "⚠️ **Paso final opcional pero recomendable**: Configura también el mensaje para tickets abiertos con:\n`/config tickets mensajes canal:" + channel_id + " tipo:ticket abierto título:<título> descripción:<descripción>`"
            
            await interaction.followup.send(
                f"<:Si:825734135116070962> Mensaje para abrir tickets enviado a {target_channel.mention}.\n\n{completion_message}",
                ephemeral=False
            )

    except Exception as e:
        print(f"Error en show_tickets_messages: {e}")
        if not interaction.response.is_done():
            await interaction.response.send_message(
                f"<:No:825734196256440340> Ocurrió un error: {str(e)}",
                ephemeral=True
            )
        else:
            await interaction.followup.send(
                f"<:No:825734196256440340> Ocurrió un error: {str(e)}",
                ephemeral=True
            )