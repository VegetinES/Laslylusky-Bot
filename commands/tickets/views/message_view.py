import discord
from discord.ext import commands
from .message_components.preview_handler import generate_preview
from .message_components.message_base_view import MessageBaseView
from .message_components.embed_handler import EmbedHandlerView
from .message_components.text_handler import TextHandlerView
from .message_components.button_handler import ButtonHandlerView

class MessageConfigView(discord.ui.View):
    def __init__(self, bot, message_type, message_config, ticket_config, ticket_channel, log_channel):
        super().__init__(timeout=300)
        self.bot = bot
        self.message_type = message_type
        self.message_config = message_config
        self.ticket_config = ticket_config
        self.ticket_channel = ticket_channel
        self.log_channel = log_channel
        
        if not message_config or not isinstance(message_config, dict):
            if message_type == "open_message":
                self.message_config = MessageBaseView.create_default_open_message()
            elif message_type == "opened_message":
                self.message_config = MessageBaseView.create_default_opened_message()
        
        self.add_message_options()
    
    def add_message_options(self):
        if not self.message_config.get("embed") and not self.message_config.get("plain_message"):
            MessageBaseView.setup_initial_options(self)
        else:
            if self.message_config.get("embed"):
                EmbedHandlerView.setup_embed_options(self)
                    
                if self.message_config.get("plain_message"):
                    TextHandlerView.add_remove_text_button(self)
                else:
                    TextHandlerView.add_text_button(self)
            else:
                TextHandlerView.setup_text_options(self)
                
            if self.message_type == "open_message":
                ButtonHandlerView.setup_button_options(self)
            elif self.message_type.startswith("opened_message"):
                if "_" in self.message_type:
                    button_id = self.message_type.split("_", 1)[1]
                    for button in self.ticket_config.get("open_message", {}).get("buttons", []):
                        if button.get("id") == button_id:
                            button_name = button.get("label", "Desconocido")
                            info_btn = discord.ui.Button(
                                style=discord.ButtonStyle.secondary,
                                label=f"Mensaje para: {button_name}",
                                disabled=True,
                                row=0
                            )
                            self.add_item(info_btn)
                            break
            
            save_btn = discord.ui.Button(
                style=discord.ButtonStyle.success,
                label="Guardar Cambios",
                emoji="💾",
                custom_id="save_message",
                row=4
            )
            save_btn.callback = self.save_callback
            self.add_item(save_btn)

            if self.message_type.startswith("opened_message") and len(self.ticket_config.get("open_message", {}).get("buttons", [])) > 1:
                change_button_btn = discord.ui.Button(
                    style=discord.ButtonStyle.primary,
                    label="Cambiar Botón",
                    emoji="🔄",
                    custom_id="change_button",
                    row=3
                )
                change_button_btn.callback = self.change_button_callback
                self.add_item(change_button_btn)
        
        MessageBaseView.add_common_buttons(self)
    
    async def change_button_callback(self, interaction):
        try:
            buttons = self.ticket_config.get("open_message", {}).get("buttons", [])
            if not buttons:
                await interaction.response.send_message(
                    "<:No:825734196256440340> No hay botones configurados.",
                    ephemeral=True
                )
                return
            
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
                    for button in buttons:
                        if button.get("id") == button_id:
                            button_label = button.get("label", "Desconocido")
                            self.ticket_config["opened_messages"][button_id] = {
                                "embed": True,
                                "title": f"Ticket de {button_label}",
                                "description": f"Gracias por abrir un ticket de {button_label}. Un miembro del equipo te atenderá lo antes posible.",
                                "footer": "",
                                "color": "green",
                                "fields": [],
                                "image": {"url": "", "enabled": False},
                                "thumbnail": {"url": "", "enabled": False},
                                "plain_message": ""
                            }
                            break
                
                message_config = self.ticket_config["opened_messages"].get(button_id, {})
                new_view = MessageConfigView(
                    self.bot, 
                    f"opened_message_{button_id}",
                    message_config,
                    self.ticket_config,
                    self.ticket_channel,
                    self.log_channel
                )
                
                preview = await generate_preview(f"opened_message_{button_id}", message_config, interaction.guild)
                
                await select_interaction.response.edit_message(
                    content=f"Configurando mensaje para tickets abiertos con el botón '{button.get('label', 'Desconocido')}'",
                    embed=preview.get("embed"),
                    view=new_view
                )
            
            select.callback = button_select_callback
            
            temp_view = discord.ui.View(timeout=60)
            temp_view.add_item(select)
            
            back_btn = discord.ui.Button(
                style=discord.ButtonStyle.secondary,
                label="Cancelar",
                custom_id="cancel_button_select"
            )
            
            async def back_callback(btn_interaction):
                await MessageBaseView.update_view_with_preview(self, btn_interaction)
            
            back_btn.callback = back_callback
            temp_view.add_item(back_btn)
            
            await interaction.response.edit_message(
                content="Selecciona el botón para el cual quieres configurar el mensaje de ticket abierto:",
                embed=None,
                view=temp_view
            )
        except Exception as e:
            print(f"Error al cambiar botón: {e}")
            await interaction.response.send_message(
                f"<:No:825734196256440340> Error al cambiar botón: {str(e)}",
                ephemeral=True
            )

    async def embed_callback(self, interaction: discord.Interaction):
        return await EmbedHandlerView.handle_embed_creation(self, interaction)
    
    async def text_callback(self, interaction: discord.Interaction):
        return await TextHandlerView.handle_text_creation(self, interaction)
    
    async def title_desc_callback(self, interaction: discord.Interaction):
        return await EmbedHandlerView.handle_title_desc_edit(self, interaction)
    
    async def footer_callback(self, interaction: discord.Interaction):
        return await EmbedHandlerView.handle_footer_edit(self, interaction)
    
    async def color_callback(self, interaction: discord.Interaction):
        return await EmbedHandlerView.handle_color_selection(self, interaction)
    
    async def image_callback(self, interaction: discord.Interaction):
        return await EmbedHandlerView.handle_image_toggle(self, interaction, "image")
    
    async def thumbnail_callback(self, interaction: discord.Interaction):
        return await EmbedHandlerView.handle_image_toggle(self, interaction, "thumbnail")
    
    async def add_field_callback(self, interaction: discord.Interaction):
        return await EmbedHandlerView.handle_field_add(self, interaction)
    
    async def manage_fields_callback(self, interaction: discord.Interaction):
        return await EmbedHandlerView.handle_fields_management(self, interaction)
    
    async def add_text_callback(self, interaction: discord.Interaction):
        return await TextHandlerView.handle_add_text(self, interaction)
    
    async def remove_text_callback(self, interaction: discord.Interaction):
        return await TextHandlerView.handle_remove_text(self, interaction)
    
    async def edit_text_callback(self, interaction: discord.Interaction):
        return await TextHandlerView.handle_edit_text(self, interaction)
    
    async def add_embed_callback(self, interaction: discord.Interaction):
        return await EmbedHandlerView.handle_embed_creation(self, interaction)
    
    async def add_button_callback(self, interaction: discord.Interaction):
        return await ButtonHandlerView.handle_button_add(self, interaction)
    
    async def manage_buttons_callback(self, interaction: discord.Interaction):
        return await ButtonHandlerView.handle_buttons_management(self, interaction)
    
    async def preview_callback(self, interaction: discord.Interaction):
        try:
            preview = await generate_preview(self.message_type, self.message_config, interaction.guild)
            
            await interaction.response.edit_message(
                content=preview.get("content"),
                embed=preview.get("embed"),
                view=self
            )
        except Exception as e:
            await interaction.response.send_message(
                f"<:No:825734196256440340> Error al generar vista previa: {str(e)}",
                ephemeral=True
            )
    
    async def save_callback(self, interaction: discord.Interaction):
        try:
            if self.message_config.get("embed") and not self.message_config.get("description"):
                await interaction.response.send_message(
                    "<:No:825734196256440340> Debes añadir una descripción al embed.",
                    ephemeral=True
                )
                return
            
            if not self.message_config.get("embed") and not self.message_config.get("plain_message"):
                await interaction.response.send_message(
                    "<:No:825734196256440340> Debes añadir contenido al mensaje.",
                    ephemeral=True
                )
                return
            
            if self.message_type == "open_message" and not self.message_config.get("buttons", []):
                self.message_config["buttons"] = [
                    {
                        "id": "default",
                        "label": "Abrir Ticket",
                        "emoji": "🎫",
                        "style": 3,
                        "name_format": "ticket-{id}"
                    }
                ]
            
            if self.message_type.startswith("opened_message_"):
                button_id = self.message_type.split("_", 1)[1]
                self.ticket_config["opened_messages"][button_id] = self.message_config
            else:
                self.ticket_config[self.message_type] = self.message_config
            
            from .edit_view import TicketEditView
            
            view = TicketEditView(self.bot, self.ticket_config, self.ticket_channel, self.log_channel)
            preview = await generate_preview(self.message_type, self.message_config, interaction.guild)
            
            await interaction.response.edit_message(
                content=f"<:Si:825734135116070962> Mensaje configurado correctamente.\n\n{preview.get('content')}",
                embed=preview.get("embed"),
                view=view
            )
        except Exception as e:
            await interaction.response.send_message(
                f"<:No:825734196256440340> Error al guardar el mensaje: {str(e)}",
                ephemeral=True
            )
    
    async def back_callback(self, interaction: discord.Interaction):
        try:
            from .edit_view import TicketEditView
            
            view = TicketEditView(self.bot, self.ticket_config, self.ticket_channel, self.log_channel)
            
            await interaction.response.edit_message(
                content=None,
                embed=discord.Embed(
                    title="Configurar Ticket",
                    description=f"Configura el ticket para el canal {self.ticket_channel.mention}",
                    color=0x3498db
                ),
                view=view
            )
        except Exception as e:
            await interaction.response.send_message(
                f"<:No:825734196256440340> Error al volver: {str(e)}",
                ephemeral=True
            )
    
    async def cancel_callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            content=None,
            embed=discord.Embed(
                title="Configuración Cancelada",
                description="<:No:825734196256440340> Has cancelado la configuración del mensaje.",
                color=0xe74c3c
            ),
            view=None
        )