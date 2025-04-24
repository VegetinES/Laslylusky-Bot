import discord
import asyncio
import traceback

async def create_ticket(interaction: discord.Interaction, channel_id, button_index=0):
    from ..database import get_ticket_data, increment_ticket_counter, update_specific_ticket_counter
    from ..preview import generate_preview
    
    print(f"Intentando crear ticket en canal {channel_id} con botón {button_index}")
    
    ticket_channel = interaction.guild.get_channel(int(channel_id))
    if ticket_channel:
        active_threads = ticket_channel.threads
        for thread in active_threads:
            if not thread.archived:
                try:
                    members = await thread.fetch_members()
                    for member in members:
                        if member.id == interaction.user.id:
                            await interaction.followup.send(
                                f"<:No:825734196256440340> Ya tienes un ticket abierto: {thread.mention}. Por favor, utiliza ese ticket o ciérralo antes de abrir uno nuevo.",
                                ephemeral=True
                            )
                            return
                except Exception as e:
                    print(f"Error al verificar miembros del ticket: {e}")
    
    ticket_config = get_ticket_data(interaction.guild.id, channel_id)

    if not ticket_config:
        print(f"No se encontró configuración de ticket para {interaction.guild.id}/{channel_id}")
        await interaction.followup.send(
            "<:No:825734196256440340> No se encontró la configuración del ticket.",
            ephemeral=True
        )
        return
    
    ticket_channel = interaction.guild.get_channel(int(channel_id))
    if not ticket_channel:
        print(f"No se encontró el canal de tickets {channel_id}")
        await interaction.followup.send(
            "<:No:825734196256440340> No se encontró el canal de tickets.",
            ephemeral=True
        )
        return
    
    buttons = ticket_config.get("open_message", {}).get("buttons", [{}])
    print(f"Número de botones configurados: {len(buttons)}")
    
    if button_index >= len(buttons):
        print(f"Índice de botón fuera de rango: {button_index}, usando botón 0")
        button_index = 0
    
    button_config = buttons[button_index]
    button_id = button_config.get("id", "default")
    print(f"Configuración de botón seleccionada: {button_config}")
    
    if "auto_increment" not in ticket_config:
        ticket_config["auto_increment"] = {}
    
    if button_id not in ticket_config["auto_increment"]:
        ticket_config["auto_increment"][button_id] = 1
    
    ticket_count = ticket_config["auto_increment"][button_id]
    ticket_config["auto_increment"][button_id] += 1
    
    await update_specific_ticket_counter(interaction.guild.id, channel_id, button_id, ticket_config["auto_increment"][button_id])
    
    name_format = button_config.get("name_format", "ticket-{id}")
    thread_name = name_format.replace("{id}", str(ticket_count))
    thread_name = thread_name.replace("{userid}", str(interaction.user.id))
    thread_name = thread_name.replace("{usertag}", interaction.user.name)
    
    print(f"Creando hilo con nombre: {thread_name}")
    
    try:
        thread = await ticket_channel.create_thread(
            name=thread_name,
            type=discord.ChannelType.private_thread,
            reason=f"Ticket creado por {interaction.user.name}"
        )
        
        await interaction.followup.send(
            f"<:Si:825734135116070962> Tu ticket ha sido creado: {thread.mention}",
            ephemeral=True
        )
        
        await thread.add_user(interaction.user)
        
        mentions = []
        
        for role_id in ticket_config.get("permissions", {}).get("manage", {}).get("roles", []):
            role = interaction.guild.get_role(int(role_id))
            if role:
                mentions.append(role.mention)
        
        for user_id in ticket_config.get("permissions", {}).get("manage", {}).get("users", []):
            try:
                user = await interaction.guild.fetch_member(int(user_id))
                if user:
                    mentions.append(user.mention)
            except:
                pass
        
        if mentions:
            await thread.send(" ".join(mentions))
        
        message_config = None
        if "opened_messages" in ticket_config and button_id in ticket_config["opened_messages"]:
            print(f"Usando mensaje específico para botón {button_id}")
            message_config = ticket_config["opened_messages"][button_id]
        else:
            print("Usando mensaje de ticket abierto por defecto")
            message_config = ticket_config.get("opened_message", {})
        
        if message_config:
            message_config["VIEW_MODE"] = True
        
        preview = await generate_preview("opened_message", message_config, interaction.guild)
        
        if message_config and "VIEW_MODE" in message_config:
            del message_config["VIEW_MODE"]
        
        class TicketControlView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)
                
                add_user_btn = discord.ui.Button(
                    style=discord.ButtonStyle.primary,
                    label="Añadir Usuario",
                    emoji="➕",
                    custom_id=f"ticket:add:{thread.id}",
                    row=0
                )
                self.add_item(add_user_btn)
                
                remove_user_btn = discord.ui.Button(
                    style=discord.ButtonStyle.primary,
                    label="Eliminar Usuario",
                    emoji="➖",
                    custom_id=f"ticket:remove:{thread.id}",
                    row=0
                )
                self.add_item(remove_user_btn)
            
                close_btn = discord.ui.Button(
                    style=discord.ButtonStyle.secondary,
                    label="Archivar Ticket",
                    emoji="🔒",
                    custom_id=f"ticket:close:{thread.id}",
                    row=0
                )
                self.add_item(close_btn)

        message = await thread.send(
            embed=preview.get("embed"),
            view=TicketControlView()
        )
        
        await message.pin()

        log_channel_id = ticket_config.get("log_channel")
        if log_channel_id:
            log_channel = interaction.guild.get_channel(int(log_channel_id))
            if log_channel:
                log_embed = discord.Embed(
                    title="Ticket Abierto",
                    description=f"Se ha creado un nuevo ticket.",
                    color=0x2ecc71
                )
                
                log_embed.add_field(name="Ticket", value=f"{thread.mention} ({thread.id})", inline=True)
                log_embed.add_field(name="Creado por", value=f"{interaction.user.mention} ({interaction.user.id})", inline=True)
                
                view = discord.ui.View()
                button = discord.ui.Button(
                    style=discord.ButtonStyle.url,
                    label="Ver Ticket",
                    url=f"https://discord.com/channels/{interaction.guild.id}/{thread.id}"
                )
                view.add_item(button)
                
                await log_channel.send(embed=log_embed, view=view)
    
    except Exception as e:
        print(f"Error al crear ticket: {e}")
        await interaction.followup.send(
            f"<:No:825734196256440340> Error al crear el ticket: {str(e)}",
            ephemeral=True
        )

async def close_ticket(interaction: discord.Interaction, thread_id):
    try:
        thread = interaction.guild.get_thread(int(thread_id))
        
        if not thread:
            await interaction.followup.send(
                "<:No:825734196256440340> No se encontró el hilo del ticket.",
                ephemeral=True
            )
            return
        
        await interaction.followup.send(
            "<:Si:825734135116070962> Este ticket será archivado en 10 segundos...",
            ephemeral=True
        )
        
        await asyncio.sleep(10)
        
        try:
            await thread.edit(archived=True, locked=False)
            
            parent_channel = thread.parent
            if parent_channel:
                from ..database import get_ticket_data
                
                ticket_config = get_ticket_data(interaction.guild.id, str(parent_channel.id))
                if ticket_config:
                    log_channel_id = ticket_config.get("log_channel")
                    if log_channel_id:
                        log_channel = interaction.guild.get_channel(int(log_channel_id))
                        if log_channel:
                            log_embed = discord.Embed(
                                title="Ticket Archivado",
                                description=f"Se ha archivado un ticket.",
                                color=0xe74c3c
                            )
                            
                            log_embed.add_field(name="Ticket", value=f"{thread.mention} ({thread.id})", inline=True)
                            log_embed.add_field(name="Archivado por", value=f"{interaction.user.mention} ({interaction.user.id})", inline=True)

                            view = discord.ui.View()
                            button = discord.ui.Button(
                                style=discord.ButtonStyle.url,
                                label="Ver Ticket",
                                url=f"https://discord.com/channels/{interaction.guild.id}/{thread.id}"
                            )
                            view.add_item(button)
                            
                            await log_channel.send(embed=log_embed, view=view)
        except Exception as e:
            print(f"Error al archivar ticket: {e}")
            await interaction.followup.send(
                f"<:No:825734196256440340> Error al archivar el ticket: {str(e)}",
                ephemeral=True
            )
    except Exception as e:
        print(f"Error en close_ticket: {e}")
        try:
            await interaction.followup.send(
                f"<:No:825734196256440340> Error al archivar el ticket: {str(e)}",
                ephemeral=True
            )
        except:
            print(f"No se pudo enviar el mensaje de error para close_ticket")