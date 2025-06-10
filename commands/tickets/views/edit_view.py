import discord
from discord.ext import commands
from ..utils.preview import generate_preview
from ..utils.modals import TicketNameModal
import asyncio

class TicketEditView(discord.ui.View):
    def __init__(self, bot, ticket_config, ticket_channel, log_channel):
        super().__init__(timeout=300)
        self.bot = bot
        self.ticket_config = ticket_config
        self.ticket_channel = ticket_channel
        self.log_channel = log_channel
        
        cancel_btn = discord.ui.Button(
            style=discord.ButtonStyle.danger,
            label="Cancelar",
            emoji="❌",
            custom_id="cancel_edit",
            row=3
        )
        cancel_btn.callback = self.cancel_callback
        self.add_item(cancel_btn)
        
        change_ticket_channel_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Cambiar Canal Tickets",
            emoji="🔄",
            custom_id="change_ticket_channel",
            row=0
        )
        change_ticket_channel_btn.callback = self.change_ticket_channel_callback
        self.add_item(change_ticket_channel_btn)
        
        change_log_channel_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Cambiar Canal Logs",
            emoji="📋",
            custom_id="change_log_channel",
            row=0
        )
        change_log_channel_btn.callback = self.change_log_channel_callback
        self.add_item(change_log_channel_btn)
        
        open_message_btn = discord.ui.Button(
            style=discord.ButtonStyle.primary,
            label="Mensaje para Abrir Ticket",
            emoji="📩",
            custom_id="open_message",
            row=1
        )
        open_message_btn.callback = self.open_message_callback
        self.add_item(open_message_btn)
        
        opened_message_btn = discord.ui.Button(
            style=discord.ButtonStyle.primary,
            label="Mensaje de Ticket Abierto",
            emoji="📨",
            custom_id="opened_message",
            row=1
        )
        opened_message_btn.callback = self.opened_message_callback
        self.add_item(opened_message_btn)
        
        permissions_btn = discord.ui.Button(
            style=discord.ButtonStyle.primary,
            label="Gestionar Permisos",
            emoji="🔒",
            custom_id="permissions",
            row=2
        )
        permissions_btn.callback = self.permissions_callback
        self.add_item(permissions_btn)
        
        save_btn = discord.ui.Button(
            style=discord.ButtonStyle.success,
            label="Guardar Cambios",
            emoji="💾",
            custom_id="save",
            row=2
        )
        save_btn.callback = self.save_callback
        self.add_item(save_btn)
        
        delete_btn = discord.ui.Button(
            style=discord.ButtonStyle.danger,
            label="Eliminar Ticket",
            emoji="🗑️",
            custom_id="delete_ticket",
            row=3
        )
        delete_btn.callback = self.delete_ticket_callback
        self.add_item(delete_btn)
        
        back_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Volver",
            emoji="⬅️",
            custom_id="back_to_manage",
            row=3
        )
        back_btn.callback = self.back_callback
        self.add_item(back_btn)
    
    async def cancel_callback(self, interaction: discord.Interaction):
        try:
            self.bot.interaction_guild = interaction.guild
            
            embed = discord.Embed(
                title="Configuración Cancelada",
                description="<:No:825734196256440340> Has cancelado la edición del ticket.",
                color=0xe74c3c
            )
            
            await interaction.response.edit_message(
                embed=embed,
                view=None
            )
        except Exception as e:
            await interaction.response.send_message(
                f"<:No:825734196256440340> Error: {str(e)}",
                ephemeral=True
            )
    
    async def change_ticket_channel_callback(self, interaction: discord.Interaction):
        try:
            self.bot.interaction_guild = interaction.guild

            channel_select = discord.ui.ChannelSelect(
                placeholder="Selecciona el nuevo canal para tickets",
                channel_types=[discord.ChannelType.text],
                custom_id="change_ticket_channel_select"
            )
            
            async def ticket_channel_callback(select_interaction):
                try:
                    channel_id = int(select_interaction.data["values"][0])
                    channel = interaction.guild.get_channel(channel_id)
                    
                    if not channel:
                        await select_interaction.response.send_message(
                            "<:No:825734196256440340> No se encontró el canal seleccionado.",
                            ephemeral=True
                        )
                        return
                    
                    self.ticket_config["ticket_channel"] = channel_id
                    self.ticket_channel = channel
                    
                    await select_interaction.response.edit_message(
                        embed=discord.Embed(
                            title="Configurar Ticket",
                            description=f"Canal para tickets actualizado: {channel.mention}\n\nContinúa con la configuración.",
                            color=0x3498db
                        ),
                        view=self
                    )
                except Exception as e:
                    await select_interaction.response.send_message(
                        f"<:No:825734196256440340> Error: {str(e)}",
                        ephemeral=True
                    )
            
            channel_select.callback = ticket_channel_callback
            
            temp_view = discord.ui.View(timeout=60)
            temp_view.add_item(channel_select)
            
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="Cambiar Canal de Tickets",
                    description="Selecciona el nuevo canal donde se crearán los tickets.",
                    color=0x3498db
                ),
                view=temp_view
            )
        except Exception as e:
            await interaction.response.send_message(
                f"<:No:825734196256440340> Error: {str(e)}",
                ephemeral=True
            )

    async def change_log_channel_callback(self, interaction: discord.Interaction):
        try:
            self.bot.interaction_guild = interaction.guild

            channel_select = discord.ui.ChannelSelect(
                placeholder="Selecciona el nuevo canal para logs",
                channel_types=[discord.ChannelType.text],
                custom_id="change_log_channel_select"
            )
            
            async def log_channel_callback(select_interaction):
                try:
                    channel_id = int(select_interaction.data["values"][0])
                    channel = interaction.guild.get_channel(channel_id)
                    
                    if not channel:
                        await select_interaction.response.send_message(
                            "<:No:825734196256440340> No se encontró el canal seleccionado.",
                            ephemeral=True
                        )
                        return
                    
                    self.ticket_config["log_channel"] = channel_id
                    self.log_channel = channel
                    
                    await select_interaction.response.edit_message(
                        embed=discord.Embed(
                            title="Configurar Ticket",
                            description=f"Canal para logs actualizado: {channel.mention}\n\nContinúa con la configuración.",
                            color=0x3498db
                        ),
                        view=self
                    )
                except Exception as e:
                    await select_interaction.response.send_message(
                        f"<:No:825734196256440340> Error: {str(e)}",
                        ephemeral=True
                    )
            
            log_channel_callback.callback = log_channel_callback
            
            temp_view = discord.ui.View(timeout=60)
            temp_view.add_item(channel_select)
            
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="Cambiar Canal de Logs",
                    description="Selecciona el nuevo canal donde se enviarán los logs de tickets.",
                    color=0x3498db
                ),
                view=temp_view
            )
        except Exception as e:
            await interaction.response.send_message(
                f"<:No:825734196256440340> Error: {str(e)}",
                ephemeral=True
            )

    async def save_callback(self, interaction: discord.Interaction):
        try:
            from ..utils.database import save_ticket_config
            
            self.bot.interaction_guild = interaction.guild
            
            if not self.ticket_config.get("permissions", {}).get("manage", {}).get("roles") and not self.ticket_config.get("permissions", {}).get("manage", {}).get("users"):
                await interaction.response.send_message(
                    "<:No:825734196256440340> Debes configurar al menos un rol o usuario con permisos de gestión.",
                    ephemeral=True
                )
                return
            
            if "open_message" not in self.ticket_config or not isinstance(self.ticket_config["open_message"], dict):
                from .message_components.message_base_view import MessageBaseView
                self.ticket_config["open_message"] = MessageBaseView.create_default_open_message()
            
            if "opened_message" not in self.ticket_config or not isinstance(self.ticket_config["opened_message"], dict):
                from .message_components.message_base_view import MessageBaseView
                self.ticket_config["opened_message"] = MessageBaseView.create_default_opened_message()
            
            await interaction.response.defer(ephemeral=False)
            
            success = await save_ticket_config(interaction.guild.id, str(self.ticket_channel.id), self.ticket_config)
            
            if success:
                embed = discord.Embed(
                    title="Configuración Guardada",
                    description="<:Si:825734135116070962> La configuración de tickets para " + 
                                f"{self.ticket_channel.mention} ha sido guardada correctamente. Los cambios se aplicarán automáticamente.",
                    color=0x2ecc71
                )
                
                await interaction.followup.edit_message(
                    message_id=interaction.message.id,
                    content=None,
                    embed=embed,
                    view=None
                )
            else:
                await interaction.followup.send(
                    "<:No:825734196256440340> Error al guardar la configuración.",
                    ephemeral=True
                )
        except Exception as e:
            print(f"Error al guardar: {e}")
            try:
                await interaction.followup.send(
                    f"<:No:825734196256440340> Error al guardar: {str(e)}",
                    ephemeral=True
                )
            except:
                pass
    
    async def open_message_callback(self, interaction: discord.Interaction):
        try:
            self.bot.interaction_guild = interaction.guild

            from .message_view import MessageConfigView
            
            message_type = "open_message"
            message_config = self.ticket_config.get(message_type, {})
            
            if not message_config or not isinstance(message_config, dict):
                from .message_components.message_base_view import MessageBaseView
                message_config = MessageBaseView.create_default_open_message()
            
            view = MessageConfigView(self.bot, message_type, message_config, self.ticket_config, self.ticket_channel, self.log_channel)
            preview = await generate_preview(message_type, message_config, interaction.guild)
            
            await interaction.response.edit_message(
                content=preview.get("content"),
                embed=preview.get("embed"),
                view=view
            )
        except Exception as e:
            await interaction.response.send_message(
                f"<:No:825734196256440340> Error al abrir la configuración del mensaje: {str(e)}",
                ephemeral=True
            )
    
    async def opened_message_callback(self, interaction: discord.Interaction):
        try:
            self.bot.interaction_guild = interaction.guild

            from .message_view import MessageConfigView
            
            buttons = self.ticket_config.get("open_message", {}).get("buttons", [])
            
            if len(buttons) > 1:
                options = []
                for button in buttons:
                    button_id = button.get("id", "unknown")
                    options.append(
                        discord.SelectOption(
                            label=button.get("label", "Botón sin nombre"),
                            value=button_id,
                            description=f"Configurar mensaje para {button.get('label', 'este botón')}"
                        )
                    )
                
                select = discord.ui.Select(
                    placeholder="Selecciona un botón para configurar su mensaje",
                    options=options,
                    custom_id="select_button_message"
                )
                
                async def button_select_callback(select_interaction):
                    button_id = select_interaction.data["values"][0]
                    
                    if "opened_messages" not in self.ticket_config:
                        self.ticket_config["opened_messages"] = {}
                    
                    if button_id not in self.ticket_config["opened_messages"]:
                        self.ticket_config["opened_messages"][button_id] = {
                            "embed": True,
                            "title": "Ticket Abierto",
                            "description": "Gracias por abrir un ticket. Un miembro del equipo te atenderá lo antes posible.",
                            "footer": "",
                            "color": "green",
                            "fields": [],
                            "image": {"url": "", "enabled": False},
                            "thumbnail": {"url": "", "enabled": False},
                            "plain_message": ""
                        }
                        
                        button_label = ""
                        for btn in buttons:
                            if btn.get("id") == button_id:
                                button_label = btn.get("label", "")
                                break
                                
                        if button_label:
                            self.ticket_config["opened_messages"][button_id]["title"] = f"Ticket de {button_label}"
                            self.ticket_config["opened_messages"][button_id]["description"] = f"Gracias por abrir un ticket de {button_label}. Un miembro del equipo te atenderá lo antes posible."
                    
                    message_config = self.ticket_config["opened_messages"][button_id]
                    
                    view = MessageConfigView(
                        self.bot, 
                        f"opened_message_{button_id}", 
                        message_config,
                        self.ticket_config,
                        self.ticket_channel,
                        self.log_channel
                    )
                    
                    from ..utils.preview import generate_preview
                    preview = await generate_preview("opened_message", message_config, select_interaction.guild)
                    
                    selected_button_label = "Desconocido"
                    for btn in buttons:
                        if btn.get("id") == button_id:
                            selected_button_label = btn.get("label", "Desconocido")
                            break
                    
                    await select_interaction.response.edit_message(
                        content=f"Configurando mensaje para tickets abiertos con el botón '{selected_button_label}'",
                        embed=preview.get("embed"),
                        view=view
                    )
                
                select.callback = button_select_callback
                
                temp_view = discord.ui.View(timeout=60)
                temp_view.add_item(select)
                
                cancel_btn = discord.ui.Button(
                    style=discord.ButtonStyle.secondary,
                    label="Cancelar",
                    custom_id="cancel_button_select"
                )
                
                async def cancel_callback(cancel_interaction):
                    await cancel_interaction.response.edit_message(
                        content=None,
                        embed=discord.Embed(
                            title="Configurar Ticket",
                            description=f"Configura el ticket para el canal {self.ticket_channel.mention}",
                            color=0x3498db
                        ),
                        view=self
                    )
                
                cancel_btn.callback = cancel_callback
                temp_view.add_item(cancel_btn)
                
                await interaction.response.edit_message(
                    content="Selecciona el botón para el cual quieres configurar el mensaje de ticket abierto:",
                    embed=None,
                    view=temp_view
                )
            else:
                message_type = "opened_message"
                
                if buttons and len(buttons) == 1:
                    button_id = buttons[0].get("id", "default")
                    if "opened_messages" not in self.ticket_config:
                        self.ticket_config["opened_messages"] = {}
                    
                    if button_id not in self.ticket_config["opened_messages"]:
                        self.ticket_config["opened_messages"][button_id] = {
                            "embed": True,
                            "title": "Ticket Abierto",
                            "description": "Gracias por abrir un ticket. Un miembro del equipo te atenderá lo antes posible.",
                            "footer": "",
                            "color": "green",
                            "fields": [],
                            "image": {"url": "", "enabled": False},
                            "thumbnail": {"url": "", "enabled": False},
                            "plain_message": ""
                        }
                        
                        button_label = buttons[0].get("label", "")
                        if button_label:
                            self.ticket_config["opened_messages"][button_id]["title"] = f"Ticket de {button_label}"
                            self.ticket_config["opened_messages"][button_id]["description"] = f"Gracias por abrir un ticket de {button_label}. Un miembro del equipo te atenderá lo antes posible."
                    
                    message_config = self.ticket_config["opened_messages"][button_id]
                    message_type = f"opened_message_{button_id}"
                else:
                    message_config = self.ticket_config.get("opened_message", {})
                    
                    if not message_config or not isinstance(message_config, dict):
                        from .message_components.message_base_view import MessageBaseView
                        message_config = MessageBaseView.create_default_opened_message()
                
                view = MessageConfigView(self.bot, message_type, message_config, self.ticket_config, self.ticket_channel, self.log_channel)
                
                from ..utils.preview import generate_preview
                preview = await generate_preview(message_type, message_config, interaction.guild)
                
                await interaction.response.edit_message(
                    content=preview.get("content"),
                    embed=preview.get("embed"),
                    view=view
                )
        except Exception as e:
            await interaction.response.send_message(
                f"<:No:825734196256440340> Error al abrir la configuración del mensaje: {str(e)}",
                ephemeral=True
            )
    
    async def permissions_callback(self, interaction: discord.Interaction):
        try:
            self.bot.interaction_guild = interaction.guild

            from .permissions_view import PermissionsView
            
            view = PermissionsView(self.bot, self.ticket_config, self.ticket_channel, self.log_channel)
            
            await interaction.response.edit_message(
                content=None,
                embed=discord.Embed(
                    title="Gestionar Permisos",
                    description=f"Configura los permisos para los tickets en {self.ticket_channel.mention}",
                    color=0x3498db
                ),
                view=view
            )
        except Exception as e:
            await interaction.response.send_message(
                f"<:No:825734196256440340> Error al abrir la configuración de permisos: {str(e)}",
                ephemeral=True
            )
            
    async def back_callback(self, interaction: discord.Interaction):
        try:
            self.bot.interaction_guild = interaction.guild

            from .manage_view import TicketsManageView
            
            view = TicketsManageView(self.bot)
            embed = discord.Embed(
                title="Gestión de Tickets",
                description="Selecciona un ticket existente para modificarlo o crea uno nuevo.",
                color=0x3498db
            )
            
            await interaction.response.edit_message(
                content=None,
                embed=embed,
                view=view
            )
        except Exception as e:
            await interaction.response.send_message(
                f"<:No:825734196256440340> Error al volver: {str(e)}",
                ephemeral=True
            )
            
    async def delete_ticket_callback(self, interaction: discord.Interaction):
        try:
            self.bot.interaction_guild = interaction.guild

            view = ConfirmDeleteView(self.bot, self.ticket_config, self.ticket_channel, self.log_channel)
            
            embed = discord.Embed(
                title="⚠️ Eliminar Configuración de Ticket",
                description=f"¿Estás seguro que deseas eliminar la configuración de ticket para {self.ticket_channel.mention}?\n\n"
                            f"Esta acción eliminará:\n"
                            f"• La configuración completa del ticket\n"
                            f"• El mensaje con los botones en el canal\n\n"
                            f"Esta acción no puede deshacerse.",
                color=0xe74c3c
            )
            
            await interaction.response.edit_message(
                content=None,
                embed=embed,
                view=view
            )
        except Exception as e:
            await interaction.response.send_message(
                f"<:No:825734196256440340> Error al mostrar confirmación: {str(e)}",
                ephemeral=True
            )

class ConfirmDeleteView(discord.ui.View):
    def __init__(self, bot, ticket_config, ticket_channel, log_channel):
        super().__init__(timeout=300)
        self.bot = bot
        self.ticket_config = ticket_config
        self.ticket_channel = ticket_channel
        self.log_channel = log_channel
        
        confirm_btn = discord.ui.Button(
            style=discord.ButtonStyle.danger,
            label="Confirmar Eliminación",
            emoji="⚠️",
            custom_id="confirm_delete",
            row=0
        )
        confirm_btn.callback = self.confirm_callback
        self.add_item(confirm_btn)
        
        cancel_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Cancelar",
            emoji="❌",
            custom_id="cancel_delete",
            row=0
        )
        cancel_btn.callback = self.cancel_callback
        self.add_item(cancel_btn)
    
    async def confirm_callback(self, interaction: discord.Interaction):
        try:
            self.bot.interaction_guild = interaction.guild

            from ..utils.database import delete_ticket_config
            
            channel_id_str = str(self.ticket_channel.id)
            print(f"Eliminando configuración de ticket para guild {interaction.guild.id}, canal {channel_id_str}")
            success = await delete_ticket_config(interaction.guild.id, channel_id_str)
            
            if success:
                embed = discord.Embed(
                    title="Configuración Eliminada",
                    description=f"<:Si:825734135116070962> La configuración de ticket para {self.ticket_channel.mention} ha sido eliminada correctamente.",
                    color=0x2ecc71
                )
                
                await interaction.response.edit_message(
                    embed=embed,
                    view=None
                )
                
                await asyncio.sleep(3)
                
                from .manage_view import TicketsManageView
                view = TicketsManageView(self.bot)
                
                embed = discord.Embed(
                    title="Gestión de Tickets",
                    description="Selecciona un ticket existente para modificarlo o crea uno nuevo.",
                    color=0x3498db
                )
                
                await interaction.message.edit(
                    embed=embed,
                    view=view
                )
            else:
                await interaction.response.send_message(
                    "<:No:825734196256440340> Error al eliminar la configuración del ticket.",
                    ephemeral=True
                )
        except Exception as e:
            print(f"Error al eliminar ticket: {e}")
            import traceback
            traceback.print_exc()
            await interaction.response.send_message(
                f"<:No:825734196256440340> Error al eliminar: {str(e)}",
                ephemeral=True
            )

    async def cancel_callback(self, interaction: discord.Interaction):
        try:
            self.bot.interaction_guild = interaction.guild

            from .edit_view import TicketEditView
            
            view = TicketEditView(self.bot, self.ticket_config, self.ticket_channel, self.log_channel)
            
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="Configurar Ticket",
                    description=f"Configura el ticket para el canal {self.ticket_channel.mention}",
                    color=0x3498db
                ),
                view=view
            )
        except Exception as e:
            await interaction.response.send_message(
                f"<:No:825734196256440340> Error al cancelar: {str(e)}",
                ephemeral=True
            )