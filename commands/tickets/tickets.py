import discord
from discord.ext import commands
from database.get import get_server_data, get_specific_field
from database.update import update_server_data
import asyncio
import re
import datetime

class TicketButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(style=discord.ButtonStyle.success, label="Abrir Ticket", emoji="🎫", custom_id="open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass

class TicketClose(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(style=discord.ButtonStyle.danger, label="Cerrar Ticket", emoji="🔒", custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass

class TicketControls(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(style=discord.ButtonStyle.secondary, label="Añadir Usuario", emoji="➕", custom_id="add_user", row=0)
    async def add_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass
        
    @discord.ui.button(style=discord.ButtonStyle.secondary, label="Eliminar Usuario", emoji="➖", custom_id="remove_user", row=0)
    async def remove_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass

class AddUserModal(discord.ui.Modal, title="Añadir Usuario"):
    user_id = discord.ui.TextInput(
        label="ID o Mención del Usuario",
        placeholder="ID del usuario o @mención",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        user_input = self.user_id.value.strip()
        
        user_id = None
        if user_input.startswith('<@') and user_input.endswith('>'):
            user_id = int(user_input.replace('!', '')[2:-1])
        else:
            try:
                user_id = int(user_input)
            except ValueError:
                await interaction.followup.send("Formato de usuario inválido. Proporciona una ID de usuario o una mención.", ephemeral=True)
                return
        
        try:
            user = await interaction.guild.fetch_member(user_id)
            if not user:
                await interaction.followup.send("No se pudo encontrar al usuario en el servidor.", ephemeral=True)
                return

            thread = interaction.channel
            if not isinstance(thread, discord.Thread):
                await interaction.followup.send("Este comando solo funciona en hilos de tickets.", ephemeral=True)
                return
            
            await thread.add_user(user)
            await interaction.followup.send(f"<:Si:825734135116070962> {user.mention} ha sido añadido al ticket.", ephemeral=False)
        
        except discord.Forbidden:
            await interaction.followup.send("No tengo permisos para añadir usuarios a este hilo.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"<:No:825734196256440340> Ocurrió un error: {str(e)}", ephemeral=True)

class RemoveUserModal(discord.ui.Modal, title="Eliminar Usuario"):
    user_id = discord.ui.TextInput(
        label="ID o Mención del Usuario",
        placeholder="ID del usuario o @mención",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        user_input = self.user_id.value.strip()

        user_id = None
        if user_input.startswith('<@') and user_input.endswith('>'):
            user_id = int(user_input.replace('!', '')[2:-1])
        else:
            try:
                user_id = int(user_input)
            except ValueError:
                await interaction.followup.send("Formato de usuario inválido. Proporciona una ID de usuario o una mención.", ephemeral=True)
                return
        
        try:
            user = await interaction.guild.fetch_member(user_id)
            if not user:
                await interaction.followup.send("No se pudo encontrar al usuario en el servidor.", ephemeral=True)
                return

            thread = interaction.channel
            if not isinstance(thread, discord.Thread):
                await interaction.followup.send("Este comando solo funciona en hilos de tickets.", ephemeral=True)
                return
            
            await thread.remove_user(user)
            await interaction.followup.send(f"<:Si:825734135116070962> {user.mention} ha sido eliminado del ticket.", ephemeral=False)
        
        except discord.Forbidden:
            await interaction.followup.send("No tengo permisos para eliminar usuarios de este hilo.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"<:No:825734196256440340> Ocurrió un error: {str(e)}", ephemeral=True)

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.add_view(TicketButton())
        bot.add_view(TicketClose())
        bot.add_view(TicketControls())
        
        self.button_refresh_task = self.bot.loop.create_task(self.refresh_buttons_task())
    
    async def refresh_buttons_task(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            try:
                await self.refresh_all_buttons()
                await asyncio.sleep(21600)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error en la tarea de actualización de botones: {e}")
                await asyncio.sleep(300)
    
    async def refresh_all_buttons(self):
        print("Iniciando actualización periódica de botones de tickets...")

        for guild in self.bot.guilds:
            try:
                server_data = get_server_data(guild.id)
                if not server_data or "tickets" not in server_data:
                    continue

                for channel_id, config in server_data["tickets"].items():
                    if not channel_id.isdigit():
                        continue

                    channel = guild.get_channel(int(channel_id))
                    if not channel:
                        continue

                    if config.get("ticket-abrir", False):
                        try:
                            async for message in channel.history(limit=50):
                                if message.author.id == self.bot.user.id and message.components:
                                    for row in message.components:
                                        for component in row.children:
                                            if isinstance(component, discord.Button) and component.custom_id.startswith("open_ticket"):
                                                class TicketButton(discord.ui.View):
                                                    def __init__(self):
                                                        super().__init__(timeout=None)
                                                        self.add_item(discord.ui.Button(
                                                            style=discord.ButtonStyle.success,
                                                            label="Abrir Ticket",
                                                            emoji="🎫",
                                                            custom_id=f"open_ticket:{channel_id}"
                                                        ))

                                                try:
                                                    await message.edit(view=TicketButton())
                                                    print(f"Botón de abrir ticket actualizado en el canal {channel.name} (ID: {channel_id})")
                                                except Exception as e:
                                                    print(f"Error al actualizar botón: {e}")
                                                break
                        except Exception as e:
                            print(f"Error al procesar canal {channel_id}: {e}")
            except Exception as e:
                print(f"Error al procesar servidor {guild.id}: {e}")
                
        print("Actualización periódica de botones completada.")
    
    def user_has_permission(self, user, guild_id, channel_id, permission_type):
        try:
            server_data = get_server_data(guild_id)
            if not server_data or "tickets" not in server_data or channel_id not in server_data["tickets"]:
                return False
            
            if user.guild_permissions.administrator:
                return True

            perms_config = server_data["tickets"][channel_id]["perms"]

            perm_keys = {
                "manage": ["manage-roles", "manage-users"],
                "see": ["see-roles", "see-users"],
                "close": ["close-roles", "close-users"],
                "add-del-usr": ["add-del-usr-roles", "add-del-usr-users"]
            }
            
            if permission_type not in perm_keys:
                return False
                
            roles_key, users_key = perm_keys[permission_type]

            if user.id in perms_config[users_key]:
                return True

            user_roles = [role.id for role in user.roles]
            return any(role_id in user_roles for role_id in perms_config[roles_key] if role_id != 0)
                
        except Exception as e:
            print(f"Error en user_has_permission: {e}")
            return False
    
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if not interaction.data:
            return

        if interaction.data.get("component_type", 0) != 2:
            return
            
        custom_id = interaction.data.get("custom_id", "")

        if custom_id.startswith("open_ticket"):
            await self.handle_open_ticket(interaction)

        elif custom_id == "close_ticket":
            await self.handle_close_ticket(interaction)

        elif custom_id == "add_user":
            await self.handle_add_user(interaction)
            
        elif custom_id == "remove_user":
            await self.handle_remove_user(interaction)
    
    async def handle_open_ticket(self, interaction: discord.Interaction):
        try:
            custom_id = interaction.data.get("custom_id", "")
            channel_id = interaction.channel.id
            
            if ":" in custom_id:
                channel_id = int(custom_id.split(":")[1])

            server_data = get_server_data(interaction.guild.id)
            if not server_data or "tickets" not in server_data or str(channel_id) not in server_data["tickets"]:
                await interaction.response.send_message(
                    "No hay configuración de tickets para este canal.",
                    ephemeral=True
                )
                return
            
            tickets_config = server_data["tickets"][str(channel_id)]

            user_has_open_ticket = False
            for guild_channel_id, channel_config in server_data["tickets"].items():
                if not guild_channel_id.isdigit():
                    continue
                    
                guild_channel = interaction.guild.get_channel(int(guild_channel_id))
                if not guild_channel:
                    continue

                for thread in guild_channel.threads:
                    if (thread.type == discord.ChannelType.private_thread and 
                        not thread.archived and 
                        interaction.user.id in [member.id for member in await thread.fetch_members()]):
                        user_has_open_ticket = True
                        break
                        
                if user_has_open_ticket:
                    break

            if user_has_open_ticket:
                await interaction.response.send_message(
                    "<:No:825734196256440340> Ya tienes un ticket abierto.",
                    ephemeral=True
                )
                return

            ticket_id = tickets_config["id"]

            ticket_name = tickets_config["tickets-name"].replace("{id}", str(ticket_id))

            main_channel = interaction.guild.get_channel(channel_id)
            if not main_channel:
                await interaction.response.send_message(
                    "No se pudo encontrar el canal configurado.",
                    ephemeral=True
                )
                return
            
            await interaction.response.defer(ephemeral=True)
            
            thread = await main_channel.create_thread(
                name=ticket_name,
                type=discord.ChannelType.private_thread,
                reason=f"Ticket abierto por {interaction.user.name}",
                invitable=False
            )

            tickets_config["id"] += 1
            update_server_data(interaction.guild.id, f"tickets/{channel_id}", tickets_config)

            async for message in thread.history(limit=10):
                if message.type == discord.MessageType.thread_created:
                    try:
                        await message.delete()
                    except discord.HTTPException:
                        pass
                    break

            users_to_add = [interaction.user]
            
            server_data = get_server_data(interaction.guild.id)
            if server_data and "tickets" in server_data and str(channel_id) in server_data["tickets"]:
                tickets_config = server_data["tickets"][str(channel_id)]
                perms_config = tickets_config.get("perms", {})

                manage_users = perms_config.get("manage-users", [0])
                see_users = perms_config.get("see-users", [0]) 
                close_users = perms_config.get("close-users", [0])
                add_del_users = perms_config.get("add-del-usr-users", [0])

                all_users = set()
                
                if manage_users != [0]:
                    all_users.update(manage_users)
                if see_users != [0]:
                    all_users.update(see_users)
                if close_users != [0]:
                    all_users.update(close_users)
                if add_del_users != [0]:
                    all_users.update(add_del_users)

                if 0 in all_users:
                    all_users.remove(0)
                if interaction.user.id in all_users:
                    all_users.remove(interaction.user.id)

                for user_id in all_users:
                    try:
                        user = await interaction.guild.fetch_member(user_id)
                        if user:
                            users_to_add.append(user)
                    except:
                        pass

                manage_roles = perms_config.get("manage-roles", [0])
                see_roles = perms_config.get("see-roles", [0])
                close_roles = perms_config.get("close-roles", [0])
                add_del_roles = perms_config.get("add-del-usr-roles", [0])
                
                all_roles = set()
                
                if manage_roles != [0]:
                    all_roles.update(manage_roles)
                if see_roles != [0]:
                    all_roles.update(see_roles)
                if close_roles != [0]:
                    all_roles.update(close_roles)
                if add_del_roles != [0]:
                    all_roles.update(add_del_roles)

                if 0 in all_roles:
                    all_roles.remove(0)

                role_users = set()
                for member in interaction.guild.members:
                    if member.id != interaction.user.id and member.id not in all_users:
                        member_role_ids = [role.id for role in member.roles]
                        if any(role_id in member_role_ids for role_id in all_roles):
                            role_users.add(member)
                
                users_to_add.extend(role_users)

            for user in users_to_add:
                try:
                    await thread.add_user(user)
                except Exception as e:
                    print(f"Error al añadir usuario {user.id} al hilo: {e}")

            await asyncio.sleep(1)

            async for message in thread.history(limit=50):
                if message.type == discord.MessageType.recipient_add:
                    try:
                        await message.delete()
                    except discord.HTTPException:
                        pass

            if tickets_config.get("ticket-abierto", {}).get("activado", False):
                ticket_data = tickets_config["ticket-abierto"]

                título = ticket_data.get("title", "Ticket Abierto")
                descripción = ticket_data.get("descripcion", "Un miembro del staff te atenderá pronto.")
                color_value = ticket_data.get("color")
                imagen_url = ticket_data.get("imagen")
                footer_text = ticket_data.get("footer")
                mensaje_text = ticket_data.get("mensaje")

                if título:
                    título = título.replace("{user}", interaction.user.mention)
                    título = título.replace("{usertag}", str(interaction.user))
                    título = título.replace("{userid}", str(interaction.user.id))
                
                if descripción:
                    descripción = descripción.replace("{user}", interaction.user.mention)
                    descripción = descripción.replace("{usertag}", str(interaction.user))
                    descripción = descripción.replace("{userid}", str(interaction.user.id))
                    descripción = descripción.replace(r"{\n}", "\n")
                
                if footer_text:
                    footer_text = footer_text.replace("{usertag}", str(interaction.user))
                    footer_text = footer_text.replace("{userid}", str(interaction.user.id))

                embed = discord.Embed(
                    title=título,
                    description=descripción,
                    color=color_value if color_value is not None else discord.Color.blue()
                )
                
                if imagen_url:
                    embed.set_image(url=imagen_url)
                
                if footer_text:
                    embed.set_footer(text=footer_text)

                embed.timestamp = datetime.datetime.utcnow()

                close_view = TicketClose()
                controls_view = TicketControls()

                if mensaje_text:
                    mensaje_text = mensaje_text.replace("{user}", interaction.user.mention)
                    mensaje_text = mensaje_text.replace("{usertag}", str(interaction.user))
                    mensaje_text = mensaje_text.replace("{userid}", str(interaction.user.id))
                    mensaje_text = mensaje_text.replace(r"{\n}", "\n")

                if mensaje_text:
                    await thread.send(mensaje_text, embed=embed, view=close_view)
                else:
                    await thread.send(embed=embed, view=close_view)
                
                await thread.send(view=controls_view)
            else:
                embed = discord.Embed(
                    title="Ticket Abierto",
                    description=f"Ticket abierto por {interaction.user.mention}. Un miembro del staff te atenderá pronto.",
                    color=discord.Color.blue(),
                    timestamp=datetime.datetime.utcnow()
                )

                close_view = TicketClose()
                controls_view = TicketControls()

                await thread.send(embed=embed, view=close_view)
                await thread.send(view=controls_view)
            
            log_channel_id = tickets_config.get("log-channel")
            if log_channel_id:
                log_channel = interaction.guild.get_channel(log_channel_id)
                if log_channel:
                    log_embed = discord.Embed(
                        title="Nuevo Ticket",
                        color=discord.Color.green(),
                        timestamp=datetime.datetime.utcnow()
                    )
                    log_embed.add_field(name="Abierto por", value=f"{interaction.user.mention}", inline=True)
                    log_embed.add_field(name="Ticket", value=f"{thread.mention}", inline=True)
                    
                    view = discord.ui.View()
                    view.add_item(discord.ui.Button(
                        style=discord.ButtonStyle.url,
                        label="Ir al Ticket",
                        url=thread.jump_url
                    ))
                    
                    await log_channel.send(embed=log_embed, view=view)
            
            await interaction.followup.send(
                f"<:Si:825734135116070962> Tu ticket ha sido creado: {thread.mention}\n\nSolo los usuarios con permisos específicos pueden ver este ticket.",
                ephemeral=True
            )
            
        except discord.Forbidden:
            await interaction.followup.send(
                "No tengo permisos para crear hilos en este canal.",
                ephemeral=True
            )
        except Exception as e:
            print(f"Error al crear ticket: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    f"<:No:825734196256440340> Ocurrió un error al crear el ticket: {str(e)}",
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    f"<:No:825734196256440340> Ocurrió un error al crear el ticket: {str(e)}",
                    ephemeral=True
                )
    
    async def handle_close_ticket(self, interaction: discord.Interaction):
        try:
            if not isinstance(interaction.channel, discord.Thread):
                await interaction.response.send_message(
                    "Este comando solo funciona en hilos de tickets.",
                    ephemeral=True
                )
                return
            
            thread = interaction.channel
            
            parent_channel = thread.parent
            if not parent_channel:
                await interaction.response.send_message(
                    "No se pudo determinar el canal padre de este hilo.",
                    ephemeral=True
                )
                return

            if not self.user_has_permission(interaction.user, interaction.guild.id, str(parent_channel.id), "close"):
                await interaction.response.send_message(
                    "No tienes permiso para cerrar tickets.",
                    ephemeral=True
                )
                return

            await interaction.response.send_message(
                "⚠️ ¿Estás seguro de que quieres cerrar este ticket? El hilo será archivado.",
                ephemeral=True,
                view=ConfirmCloseView(self.bot, thread, parent_channel.id, interaction.user)
            )
            
        except Exception as e:
            print(f"Error al cerrar ticket: {e}")
            await interaction.response.send_message(
                f"<:No:825734196256440340> Ocurrió un error al cerrar el ticket: {str(e)}",
                ephemeral=True
            )
    
    async def handle_add_user(self, interaction: discord.Interaction):
        try:
            if not isinstance(interaction.channel, discord.Thread):
                await interaction.response.send_message(
                    "Este comando solo funciona en hilos de tickets.",
                    ephemeral=True
                )
                return
            
            thread = interaction.channel

            parent_channel = thread.parent
            if not parent_channel:
                await interaction.response.send_message(
                    "No se pudo determinar el canal padre de este hilo.",
                    ephemeral=True
                )
                return

            if not self.user_has_permission(interaction.user, interaction.guild.id, str(parent_channel.id), "add-del-usr"):
                await interaction.response.send_message(
                    "No tienes permiso para añadir usuarios a tickets.",
                    ephemeral=True
                )
                return

            await interaction.response.send_modal(AddUserModal())
            
        except Exception as e:
            print(f"Error al añadir usuario: {e}")
            await interaction.response.send_message(
                f"<:No:825734196256440340> Ocurrió un error: {str(e)}",
                ephemeral=True
            )
            
    async def handle_remove_user(self, interaction: discord.Interaction):
        try:
            if not isinstance(interaction.channel, discord.Thread):
                await interaction.response.send_message(
                    "Este comando solo funciona en hilos de tickets.",
                    ephemeral=True
                )
                return
            
            thread = interaction.channel

            parent_channel = thread.parent
            if not parent_channel:
                await interaction.response.send_message(
                    "No se pudo determinar el canal padre de este hilo.",
                    ephemeral=True
                )
                return

            if not self.user_has_permission(interaction.user, interaction.guild.id, str(parent_channel.id), "add-del-usr"):
                await interaction.response.send_message(
                    "No tienes permiso para eliminar usuarios de tickets.",
                    ephemeral=True
                )
                return
            
            await interaction.response.send_modal(RemoveUserModal())
            
        except Exception as e:
            print(f"Error al eliminar usuario: {e}")
            await interaction.response.send_message(
                f"❌ Ocurrió un error: {str(e)}",
                ephemeral=True
            )
    
    def cog_unload(self):
        if hasattr(self, 'button_refresh_task'):
            self.button_refresh_task.cancel()

class ConfirmCloseView(discord.ui.View):
    def __init__(self, bot, thread, parent_channel_id, user_closer):
        super().__init__(timeout=60)
        self.bot = bot
        self.thread = thread
        self.parent_channel_id = parent_channel_id
        self.user_closer = user_closer
        self.message = None
    
    @discord.ui.button(label="Confirmar", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.defer(ephemeral=True)
            
            thread_name = self.thread.name
            new_name = thread_name
            if not thread_name.startswith("[Cerrado] "):
                new_name = f"[Cerrado] {thread_name}"
                if len(new_name) <= 100:
                    await self.thread.edit(name=new_name)
            
            closing_embed = discord.Embed(
                title="Ticket Cerrado",
                description=f"Este ticket ha sido cerrado por {self.user_closer.mention}.\nEl ticket se cerrará en 10 segundos.",
                color=discord.Color.red()
            )
            await self.thread.send(embed=closing_embed)

            guild = interaction.guild
            server_data = get_server_data(guild.id)
            if server_data and "tickets" in server_data and str(self.parent_channel_id) in server_data["tickets"]:
                log_channel_id = server_data["tickets"][str(self.parent_channel_id)].get("log-channel")
                if log_channel_id:
                    log_channel = guild.get_channel(log_channel_id)
                    if log_channel:
                        log_embed = discord.Embed(
                            title="Ticket Cerrado",
                            color=discord.Color.red(),
                            timestamp=datetime.datetime.utcnow()
                        )
                        log_embed.add_field(name="Cerrado por", value=f"{self.user_closer.mention}", inline=True)
                        log_embed.add_field(name="Ticket", value=f"{self.thread.mention}", inline=True)

                        view = discord.ui.View()
                        view.add_item(discord.ui.Button(
                            style=discord.ButtonStyle.url,
                            label="Ir al Ticket",
                            url=self.thread.jump_url
                        ))
                        
                        await log_channel.send(embed=log_embed, view=view)

            members = []
            try:
                thread_members = await self.thread.fetch_members()
                for member in thread_members:
                    if member.id != self.bot.user.id:
                        members.append(member.id)
                
                for member_id in members:
                    try:
                        member = await guild.fetch_member(member_id)
                        if member:
                            await self.thread.remove_user(member)
                    except Exception as e:
                        print(f"Error al eliminar miembro {member_id}: {e}")
            except Exception as e:
                print(f"Error al obtener miembros del hilo: {e}")

            await asyncio.sleep(10)

            await self.thread.edit(archived=True, locked=True)

            await interaction.followup.send(
                "<:Si:825734135116070962> El ticket ha sido cerrado y archivado. Sólo los moderadores pueden ver los tickets archivados.",
                ephemeral=True
            )

            for child in self.children:
                child.disabled = True
            
            await interaction.edit_original_response(view=self)
            
        except Exception as e:
            print(f"Error al confirmar cierre: {e}")
            await interaction.followup.send(
                f"<:No:825734196256440340> Ocurrió un error al cerrar el ticket: {str(e)}",
                ephemeral=True
            )
    
    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        for child in self.children:
            child.disabled = True
        
        await interaction.response.edit_message(
            content="<:No:825734196256440340> Cierre de ticket cancelado.",
            view=self
        )
    
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        
        try:
            if hasattr(self, 'message') and self.message:
                await self.message.edit(view=self)
        except Exception as e:
            print(f"Error en timeout del view de cierre: {e}")

async def setup(bot):
    await bot.add_cog(Tickets(bot))