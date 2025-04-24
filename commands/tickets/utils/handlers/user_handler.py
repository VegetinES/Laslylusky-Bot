import discord

async def add_user_to_ticket(interaction: discord.Interaction, thread_id):
    try:
        thread = interaction.guild.get_thread(int(thread_id))
        
        if not thread:
            await interaction.followup.send(
                "<:No:825734196256440340> No se encontró el hilo del ticket.",
                ephemeral=True
            )
            return
        
        class UserSelectView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=60)
                
                user_select = discord.ui.UserSelect(
                    placeholder="Selecciona un usuario para añadir",
                    min_values=1,
                    max_values=1
                )
                
                async def user_select_callback(select_interaction):
                    await add_selected_user(select_interaction, thread, thread_id)
                
                user_select.callback = user_select_callback
                self.add_item(user_select)
        
        await interaction.followup.send(
            "Selecciona un usuario para añadir al ticket:",
            view=UserSelectView(),
            ephemeral=True
        )
    except Exception as e:
        print(f"Error en add_user_to_ticket: {e}")
        await interaction.followup.send(
            f"<:No:825734196256440340> Error: {str(e)}",
            ephemeral=True
        )

async def remove_user_from_ticket(interaction: discord.Interaction, thread_id):
    try:
        thread = interaction.guild.get_thread(int(thread_id))
        
        if not thread:
            await interaction.followup.send(
                "<:No:825734196256440340> No se encontró el hilo del ticket.",
                ephemeral=True
            )
            return
        
        class UserRemoveView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=60)
                
                user_select = discord.ui.UserSelect(
                    placeholder="Selecciona un usuario para eliminar",
                    min_values=1,
                    max_values=1
                )
                
                async def user_select_callback(select_interaction):
                    await remove_selected_user(select_interaction, thread, thread_id)
                
                user_select.callback = user_select_callback
                self.add_item(user_select)
        
        await interaction.followup.send(
            "Selecciona un usuario para eliminar del ticket:",
            view=UserRemoveView(),
            ephemeral=True
        )
    except Exception as e:
        print(f"Error en remove_user_from_ticket: {e}")
        await interaction.followup.send(
            f"<:No:825734196256440340> Error: {str(e)}",
            ephemeral=True
        )

async def add_selected_user(interaction, thread, thread_id):
    try:
        selected_users = interaction.data.get("values")
        if not selected_users:
            selected_users = [user.id for user in interaction.data.get("resolved", {}).get("users", {}).values()]
        
        if not selected_users:
            await interaction.response.send_message(
                "<:No:825734196256440340> No se seleccionó ningún usuario.",
                ephemeral=True
            )
            return
        
        user_id = int(selected_users[0])
        user = interaction.guild.get_member(user_id)
        
        if not user:
            await interaction.response.send_message(
                "<:No:825734196256440340> No se encontró al usuario.",
                ephemeral=True
            )
            return
        
        try:
            await thread.add_user(user)
            await interaction.response.send_message(
                f"<:Si:825734135116070962> Usuario {user.mention} añadido al ticket.",
                ephemeral=True
            )
            
            parent_channel = thread.parent
            if parent_channel:
                from ..database import get_ticket_data
                
                ticket_config = get_ticket_data(interaction.guild.id, str(parent_channel.id))
                if ticket_config:
                    log_channel_id = ticket_config.get("log_channel")
                    if log_channel_id:
                        log_channel = interaction.guild.get_channel(int(log_channel_id))
                        if log_channel:
                            pass
        except Exception as e:
            await interaction.response.send_message(
                f"<:No:825734196256440340> Error al añadir usuario: {str(e)}",
                ephemeral=True
            )
    except Exception as e:
        print(f"Error en add_selected_user: {e}")
        await interaction.response.send_message(
            f"<:No:825734196256440340> Error: {str(e)}",
            ephemeral=True
        )

async def remove_selected_user(interaction, thread, thread_id):
    try:
        selected_users = interaction.data.get("values")
        if not selected_users:
            selected_users = [user.id for user in interaction.data.get("resolved", {}).get("users", {}).values()]
        
        if not selected_users:
            await interaction.response.send_message(
                "<:No:825734196256440340> No se seleccionó ningún usuario.",
                ephemeral=True
            )
            return
        
        user_id = int(selected_users[0])
        user = interaction.guild.get_member(user_id)
        
        if not user:
            await interaction.response.send_message(
                "<:No:825734196256440340> No se encontró al usuario.",
                ephemeral=True
            )
            return
        
        is_member = False
        try:
            thread_members = await thread.fetch_members()
            for member in thread_members:
                if member.id == user_id:
                    is_member = True
                    break
        except Exception as e:
            print(f"Error al verificar miembros del ticket: {e}")
        
        if not is_member:
            await interaction.response.send_message(
                f"<:No:825734196256440340> El usuario {user.mention} no está en este ticket.",
                ephemeral=True
            )
            return
            
        try:
            await thread.remove_user(user)
            await interaction.response.send_message(
                f"<:Si:825734135116070962> Usuario {user.mention} eliminado del ticket.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"<:No:825734196256440340> Error al eliminar usuario: {str(e)}",
                ephemeral=True
            )
    except Exception as e:
        print(f"Error en remove_selected_user: {e}")
        await interaction.response.send_message(
            f"<:No:825734196256440340> Error: {str(e)}",
            ephemeral=True
        )

async def reopen_ticket(thread, user):
    try:
        await thread.edit(archived=False)
        
        parent_channel = thread.parent
        if parent_channel:
            from ..database import get_ticket_data
            
            ticket_config = get_ticket_data(thread.guild.id, str(parent_channel.id))
            if ticket_config:
                await thread.send(
                    f"<:Si:825734135116070962> Ticket reabierto por {user.mention}."
                )
                
                log_channel_id = ticket_config.get("log_channel")
                if log_channel_id:
                    log_channel = thread.guild.get_channel(int(log_channel_id))
                    if log_channel:
                        log_embed = discord.Embed(
                            title="Ticket Reabierto",
                            description=f"Se ha reabierto un ticket que estaba archivado.",
                            color=0x2ecc71
                        )
                        
                        log_embed.add_field(name="Ticket", value=thread.mention, inline=True)
                        log_embed.add_field(name="Reabierto por", value=user.mention, inline=True)
                        log_embed.add_field(name="ID", value=f"`{thread.id}`", inline=True)
                        
                        view = discord.ui.View()
                        button = discord.ui.Button(
                            style=discord.ButtonStyle.url,
                            label="Ver Ticket",
                            url=f"https://discord.com/channels/{thread.guild.id}/{thread.id}"
                        )
                        view.add_item(button)
                        
                        await log_channel.send(embed=log_embed, view=view)
                
    except Exception as e:
        print(f"Error al reabrir ticket: {e}")