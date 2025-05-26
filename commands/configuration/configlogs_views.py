import discord
from database.update import update_server_data
from .configlogs_constants import LOG_TYPES, COLORS
from .configlogs_modals import (
    TextMessageModal, EmbedTitleDescriptionModal, EmbedFooterModal,
    FieldModal, ImageParamModal
)
from .configlogs_models import LogMessageModel

class LogConfigView(discord.ui.View):
    def __init__(self, interaction, guild_id, log_type, config_data):
        super().__init__(timeout=60)
        self.interaction = interaction
        self.guild_id = guild_id
        self.log_type = log_type
        self.config_data = config_data
        self.channel_id = config_data.get("log_channel", 0)
        self.message_data = config_data.get("message", {})
        self.activated = config_data.get("activated", False)
        
        self.update_buttons()
    
    def update_buttons(self):
        self.clear_items()
        
        if self.activated:
            deactivate_btn = discord.ui.Button(
                style=discord.ButtonStyle.danger,
                label="Desactivar",
                custom_id="deactivate"
            )
            deactivate_btn.callback = self.deactivate_callback
            self.add_item(deactivate_btn)

            modify_btn = discord.ui.Button(
                style=discord.ButtonStyle.primary,
                label="Modificar",
                custom_id="modify"
            )
            modify_btn.callback = self.modify_callback
            self.add_item(modify_btn)
        else:
            activate_btn = discord.ui.Button(
                style=discord.ButtonStyle.success,
                label="Activar",
                custom_id="activate"
            )
            activate_btn.callback = self.activate_callback
            self.add_item(activate_btn)
        
        cancel_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Cancelar",
            custom_id="cancel_main"
        )
        cancel_btn.callback = self.cancel_callback
        self.add_item(cancel_btn)
    
    async def cancel_callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            content=f"<:No:825734196256440340> Operación cancelada para **{LOG_TYPES[self.log_type]['name']}**.",
            embed=None,
            view=None
        )
    
    async def deactivate_callback(self, interaction: discord.Interaction):
        view = ConfirmView(interaction, self.guild_id, self.log_type, self.config_data)
        await interaction.response.edit_message(
            content=f"⚠️ ¿Estás seguro que deseas desactivar los {LOG_TYPES[self.log_type]['name']}?",
            embed=None,
            view=view
        )
    
    async def activate_callback(self, interaction: discord.Interaction):
        message_is_configured = False
        
        if isinstance(self.message_data, dict):
            if self.message_data.get("embed", False):
                message_is_configured = bool(self.message_data.get("description", ""))
            else:
                message_is_configured = bool(self.message_data.get("message", ""))
        
        if self.channel_id and self.channel_id != 0 and message_is_configured:
            update_data = {
                "activated": True
            }
            
            if update_server_data(self.guild_id, f"audit_logs/{self.log_type}", update_data):
                self.activated = True
                self.config_data["activated"] = True
                
                channel = interaction.guild.get_channel(self.channel_id)
                
                from .configlogs_preview import create_preview
                preview_data = await create_preview(self.log_type, self.message_data, interaction.guild)
                
                detail_view = LogConfigDetailView(
                    interaction, 
                    self.guild_id, 
                    self.log_type, 
                    self.config_data,
                    self.message_data
                )
                
                await interaction.response.edit_message(
                    content=f"<:Si:825734135116070962> **{LOG_TYPES[self.log_type]['name']}** han sido activados correctamente.\n\n{preview_data['content']}",
                    embed=preview_data.get("embed"),
                    view=detail_view
                )
        else:
            channel_select = discord.ui.ChannelSelect(
                channel_types=[discord.ChannelType.text],
                placeholder="Selecciona un canal para los logs",
                min_values=1,
                max_values=1
            )
            
            async def channel_select_callback(select_interaction):
                selected_channel = select_interaction.data["values"][0]
                channel = interaction.guild.get_channel(int(selected_channel))
                
                if not channel:
                    await select_interaction.response.send_message("Error al seleccionar el canal.", ephemeral=True)
                    return
                
                self.channel_id = channel.id
                self.config_data["log_channel"] = channel.id
                
                update_server_data(self.guild_id, f"audit_logs/{self.log_type}", {"log_channel": channel.id})
                
                message_type_view = MessageTypeView(interaction, self.guild_id, self.log_type, self.config_data)
                await select_interaction.response.edit_message(
                    content=f"Canal seleccionado: {channel.mention}\n\nAhora selecciona el tipo de mensaje para {LOG_TYPES[self.log_type]['name']}:",
                    view=message_type_view
                )
            
            channel_select.callback = channel_select_callback
            
            setup_view = discord.ui.View(timeout=60)
            setup_view.add_item(channel_select)
            
            cancel_btn = discord.ui.Button(
                style=discord.ButtonStyle.secondary,
                label="Cancelar",
                custom_id="cancel_setup"
            )
            
            async def cancel_setup_callback(cancel_interaction):
                await cancel_interaction.response.edit_message(
                    content=f"<:No:825734196256440340> Configuración cancelada para **{LOG_TYPES[self.log_type]['name']}**.",
                    embed=None,
                    view=None
                )
            
            cancel_btn.callback = cancel_setup_callback
            setup_view.add_item(cancel_btn)
            
            await interaction.response.edit_message(
                content=f"Para activar los **{LOG_TYPES[self.log_type]['name']}**, primero selecciona el canal donde se enviarán:",
                embed=None,
                view=setup_view
            )
    
    async def modify_callback(self, interaction: discord.Interaction):
        channel = interaction.guild.get_channel(self.channel_id)
        if not channel:
            await interaction.response.send_message("El canal configurado ya no existe. Por favor, configura un nuevo canal.", ephemeral=True)
            return
        
        from .configlogs_preview import create_preview
        preview_data = await create_preview(self.log_type, self.message_data, interaction.guild)
        
        view = LogConfigDetailView(
            interaction, 
            self.guild_id, 
            self.log_type, 
            self.config_data,
            self.message_data
        )
        
        await interaction.response.edit_message(
            content=preview_data["content"],
            embed=preview_data.get("embed"),
            view=view
        )


class LogConfigDetailView(discord.ui.View):
    def __init__(self, interaction, guild_id, log_type, config_data, message_config=None):
        super().__init__(timeout=120)
        self.interaction = interaction
        self.guild_id = guild_id
        self.log_type = log_type
        self.config_data = config_data
        self.channel_id = config_data.get("log_channel", 0)
        self.activated = config_data.get("activated", False)
        
        self.message_config = message_config if message_config is not None else config_data.get("message", LogMessageModel.create_default())
        
        self._init_buttons()
    
    def _init_buttons(self):
        self.clear_items()
        
        if self.message_config.get("embed", False):
            change_type_btn = discord.ui.Button(
                style=discord.ButtonStyle.secondary,
                label="Cambiar a mensaje normal",
                custom_id="to_normal",
                row=0
            )
            change_type_btn.callback = self.to_normal_callback
            self.add_item(change_type_btn)
            
            title_desc_btn = discord.ui.Button(
                style=discord.ButtonStyle.primary,
                label="Título y descripción",
                custom_id="title_desc",
                row=0
            )
            title_desc_btn.callback = self.title_desc_callback
            self.add_item(title_desc_btn)
            
            footer_btn = discord.ui.Button(
                style=discord.ButtonStyle.primary,
                label="Footer",
                custom_id="footer",
                row=0
            )
            footer_btn.callback = self.footer_callback
            self.add_item(footer_btn)
            
            color_btn = discord.ui.Button(
                style=discord.ButtonStyle.secondary,
                label="Color",
                custom_id="color",
                row=1
            )
            color_btn.callback = self.color_callback
            self.add_item(color_btn)
            
            if self.message_config.get("thumbnail", {}).get("has", False):
                thumbnail_btn = discord.ui.Button(
                    style=discord.ButtonStyle.success,
                    label="Thumbnail",
                    emoji="✅",
                    custom_id="thumbnail",
                    row=1
                )
            else:
                thumbnail_btn = discord.ui.Button(
                    style=discord.ButtonStyle.secondary,
                    label="Thumbnail",
                    emoji="❌",
                    custom_id="thumbnail",
                    row=1
                )
            thumbnail_btn.callback = self.thumbnail_callback
            self.add_item(thumbnail_btn)
            
            if self.message_config.get("image", {}).get("has", False):
                image_btn = discord.ui.Button(
                    style=discord.ButtonStyle.success,
                    label="Imagen",
                    emoji="✅",
                    custom_id="image",
                    row=1
                )
            else:
                image_btn = discord.ui.Button(
                    style=discord.ButtonStyle.secondary,
                    label="Imagen",
                    emoji="❌",
                    custom_id="image",
                    row=1
                )
            image_btn.callback = self.image_callback
            self.add_item(image_btn)
            
            if self.log_type in ["mod_ch", "mod_cat"]:
                track_name = self.message_config.get("changedname", False)
                track_perms = self.message_config.get("changedperms", False)
                
                name_btn = discord.ui.Button(
                    style=discord.ButtonStyle.success if track_name else discord.ButtonStyle.secondary,
                    label="Cambios de nombre",
                    emoji="✅" if track_name else "❌",
                    custom_id="track_name",
                    row=2
                )
                name_btn.callback = self.track_name_callback
                self.add_item(name_btn)
                
                perms_btn = discord.ui.Button(
                    style=discord.ButtonStyle.success if track_perms else discord.ButtonStyle.secondary,
                    label="Cambios de permisos",
                    emoji="✅" if track_perms else "❌",
                    custom_id="track_perms",
                    row=2
                )
                perms_btn.callback = self.track_perms_callback
                self.add_item(perms_btn)
            
            add_field_btn = discord.ui.Button(
                style=discord.ButtonStyle.success,
                label="Añadir campo",
                emoji="➕",
                custom_id="add_field",
                row=3 if self.log_type in ["mod_ch", "mod_cat"] else 2
            )
            add_field_btn.callback = self.add_field_callback
            self.add_item(add_field_btn)
            
            if self.message_config.get("fields"):
                manage_fields_btn = discord.ui.Button(
                    style=discord.ButtonStyle.primary,
                    label="Gestionar campos",
                    custom_id="manage_fields",
                    row=3 if self.log_type in ["mod_ch", "mod_cat"] else 2
                )
                manage_fields_btn.callback = self.manage_fields_callback
                self.add_item(manage_fields_btn)
            
        else:
            change_type_btn = discord.ui.Button(
                style=discord.ButtonStyle.secondary,
                label="Cambiar a mensaje embed",
                custom_id="to_embed",
                row=0
            )
            change_type_btn.callback = self.to_embed_callback
            self.add_item(change_type_btn)
            
            modify_msg_btn = discord.ui.Button(
                style=discord.ButtonStyle.primary,
                label="Modificar mensaje",
                custom_id="modify_msg",
                row=0
            )
            modify_msg_btn.callback = self.modify_msg_callback
            self.add_item(modify_msg_btn)
            
            # Añadir opciones específicas para logs de canales/categorías modificados
            if self.log_type in ["mod_ch", "mod_cat"]:
                track_name = self.message_config.get("changedname", False)
                track_perms = self.message_config.get("changedperms", False)
                
                name_btn = discord.ui.Button(
                    style=discord.ButtonStyle.success if track_name else discord.ButtonStyle.secondary,
                    label="Cambios de nombre",
                    emoji="✅" if track_name else "❌",
                    custom_id="track_name",
                    row=1
                )
                name_btn.callback = self.track_name_callback
                self.add_item(name_btn)
                
                perms_btn = discord.ui.Button(
                    style=discord.ButtonStyle.success if track_perms else discord.ButtonStyle.secondary,
                    label="Cambios de permisos",
                    emoji="✅" if track_perms else "❌",
                    custom_id="track_perms",
                    row=1
                )
                perms_btn.callback = self.track_perms_callback
                self.add_item(perms_btn)
        
        change_channel_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Cambiar canal",
            custom_id="change_channel",
            row=4 if self.log_type in ["mod_ch", "mod_cat"] else 3
        )
        change_channel_btn.callback = self.change_channel_callback
        self.add_item(change_channel_btn)
        
        save_btn = discord.ui.Button(
            style=discord.ButtonStyle.success,
            label="Guardar cambios",
            custom_id="save",
            row=4 if self.log_type in ["mod_ch", "mod_cat"] else 3
        )
        save_btn.callback = self.save_callback
        self.add_item(save_btn)
        
        cancel_btn = discord.ui.Button(
            style=discord.ButtonStyle.danger,
            label="Cancelar",
            custom_id="cancel_detail",
            row=4 if self.log_type in ["mod_ch", "mod_cat"] else 3
        )
        cancel_btn.callback = self.cancel_callback
        self.add_item(cancel_btn)
    
    async def cancel_callback(self, interaction: discord.Interaction):
        from database.get import get_specific_field
        actual_config = get_specific_field(self.guild_id, f"audit_logs/{self.log_type}")
        
        view = LogConfigView(self.interaction, self.guild_id, self.log_type, actual_config)
        
        from .configlogs_preview import create_preview
        preview_data = await create_preview(self.log_type, actual_config.get("message", {}), interaction.guild)
        
        await interaction.response.edit_message(
            content=f"<:No:825734196256440340> Modificación cancelada para **{LOG_TYPES[self.log_type]['name']}**.\n\n{preview_data['content']}",
            embed=preview_data.get("embed"),
            view=view
        )
    
    async def to_normal_callback(self, interaction: discord.Interaction):
        self.message_config = LogMessageModel.create_default()
        self.message_config["embed"] = False
        
        modal = TextMessageModal(self.log_type)
        await interaction.response.send_modal(modal)
    
    async def to_embed_callback(self, interaction: discord.Interaction):
        self.message_config = LogMessageModel.create_default()
        self.message_config["embed"] = True
        
        modal = EmbedTitleDescriptionModal(self.log_type)
        await interaction.response.send_modal(modal)
    
    async def title_desc_callback(self, interaction: discord.Interaction):
        modal = EmbedTitleDescriptionModal(
            self.log_type,
            current_title=self.message_config.get("title", ""),
            current_description=self.message_config.get("description", ""),
            message_config=self.message_config
        )
        await interaction.response.send_modal(modal)
    
    async def footer_callback(self, interaction: discord.Interaction):
        modal = EmbedFooterModal(
            self.log_type,
            current_footer=self.message_config.get("footer", ""),
            message_config=self.message_config
        )
        await interaction.response.send_modal(modal)
    
    async def color_callback(self, interaction: discord.Interaction):
        color_view = ColorSelectView(
            self.interaction, 
            self.guild_id, 
            self.log_type, 
            self.config_data,
            self.message_config
        )
        
        await interaction.response.edit_message(
            content="Selecciona un color para el embed:",
            embed=None,
            view=color_view
        )
    
    async def thumbnail_callback(self, interaction: discord.Interaction):
        if not self.message_config.get("thumbnail", {}).get("has", False):
            modal = ImageParamModal(
                self.log_type,
                "thumbnail",
                current_param=self.message_config.get("thumbnail", {}).get("param", ""),
                message_config=self.message_config
            )
            await interaction.response.send_modal(modal)
        else:
            view = ConfirmImageView(
                "thumbnail",
                self.interaction,
                self.guild_id,
                self.log_type,
                self.config_data,
                self.message_config
            )
            await interaction.response.edit_message(
                content="¿Estás seguro que deseas desactivar el thumbnail?",
                embed=None,
                view=view
            )
    
    async def image_callback(self, interaction: discord.Interaction):
        if not self.message_config.get("image", {}).get("has", False):
            modal = ImageParamModal(
                self.log_type,
                "image",
                current_param=self.message_config.get("image", {}).get("param", ""),
                message_config=self.message_config
            )
            await interaction.response.send_modal(modal)
        else:
            view = ConfirmImageView(
                "image",
                self.interaction,
                self.guild_id,
                self.log_type,
                self.config_data,
                self.message_config
            )
            await interaction.response.edit_message(
                content="¿Estás seguro que deseas desactivar la imagen?",
                embed=None,
                view=view
            )
            
    async def track_name_callback(self, interaction: discord.Interaction):
        try:
            current_value = self.message_config.get("changedname", False)
            self.message_config["changedname"] = not current_value
            
            self.config_data["changedname"] = not current_value
            
            from .configlogs_preview import create_preview
            preview_data = await create_preview(self.log_type, self.message_config, interaction.guild)
            
            new_view = LogConfigDetailView(
                self.interaction, 
                self.guild_id, 
                self.log_type, 
                self.config_data,
                self.message_config
            )
            
            status = "activado" if self.message_config["changedname"] else "desactivado"
            
            await interaction.response.edit_message(
                content=f"<:Si:825734135116070962> Seguimiento de cambios de nombre {status}.\n\n{preview_data['content']}",
                embed=preview_data.get("embed"),
                view=new_view
            )
        except Exception as e:
            print(f"Error al actualizar seguimiento de nombre: {e}")
            await interaction.response.send_message(
                f"<:No:825734196256440340> Error al actualizar la configuración: {str(e)}",
                ephemeral=True
            )

    async def track_perms_callback(self, interaction: discord.Interaction):
        try:
            current_value = self.message_config.get("changedperms", False)
            self.message_config["changedperms"] = not current_value
            
            self.config_data["changedperms"] = not current_value
            
            from .configlogs_preview import create_preview
            preview_data = await create_preview(self.log_type, self.message_config, interaction.guild)
            
            new_view = LogConfigDetailView(
                self.interaction, 
                self.guild_id, 
                self.log_type, 
                self.config_data,
                self.message_config
            )
            
            status = "activado" if self.message_config["changedperms"] else "desactivado"
            
            await interaction.response.edit_message(
                content=f"<:Si:825734135116070962> Seguimiento de cambios de permisos {status}.\n\n{preview_data['content']}",
                embed=preview_data.get("embed"),
                view=new_view
            )
        except Exception as e:
            print(f"Error al actualizar seguimiento de permisos: {e}")
            await interaction.response.send_message(
                f"<:No:825734196256440340> Error al actualizar la configuración: {str(e)}",
                ephemeral=True
            )
    
    async def manage_fields_callback(self, interaction: discord.Interaction):
        fields_view = FieldsManagementView(
            self.interaction,
            self.guild_id,
            self.log_type,
            self.config_data,
            self.message_config
        )
        await interaction.response.edit_message(
            content=f"**Gestión de campos para {LOG_TYPES[self.log_type]['name']}**\nSelecciona un campo para editarlo o eliminarlo:",
            embed=None,
            view=fields_view
        )
    
    async def add_field_callback(self, interaction: discord.Interaction):
        if not isinstance(self.message_config.get("fields"), dict):
            self.message_config["fields"] = {}
            
        fields = self.message_config["fields"]
        
        if len(fields) >= 25:
            await interaction.response.send_message(
                "<:No:825734196256440340> Ya has alcanzado el límite máximo de campos (25).",
                ephemeral=True
            )
            return
        
        next_id = 1
        if fields:
            try:
                numeric_ids = [int(key) for key in fields.keys() if str(key).isdigit()]
                if numeric_ids:
                    next_id = max(numeric_ids) + 1
            except Exception:
                next_id = len(fields) + 1
        
        modal = FieldModal(
            self.log_type, 
            next_id,
            message_config=self.message_config
        )
        await interaction.response.send_modal(modal)
    
    async def modify_msg_callback(self, interaction: discord.Interaction):
        if not self.message_config.get("embed", False):
            modal = TextMessageModal(
                self.log_type,
                current_message=self.message_config.get("message", ""),
                message_config=self.message_config
            )
            await interaction.response.send_modal(modal)
    
    async def change_channel_callback(self, interaction: discord.Interaction):
        channel_select = discord.ui.ChannelSelect(
            channel_types=[discord.ChannelType.text],
            placeholder="Selecciona el nuevo canal para los logs",
            min_values=1,
            max_values=1
        )
        
        async def channel_callback(select_interaction):
            selected_channel = select_interaction.data["values"][0]
            channel = interaction.guild.get_channel(int(selected_channel))
            
            if not channel:
                await select_interaction.response.send_message("Error al seleccionar el canal.", ephemeral=True)
                return
            
            self.channel_id = channel.id
            self.config_data["log_channel"] = channel.id
            
            from .configlogs_preview import create_preview
            preview_data = await create_preview(self.log_type, self.message_config, interaction.guild)
            
            await select_interaction.response.edit_message(
                content=f"Canal cambiado a: {channel.mention}\n{preview_data['content']}",
                embed=preview_data.get("embed"),
                view=self
            )
        
        channel_select.callback = channel_callback
        
        temp_view = discord.ui.View(timeout=60)
        temp_view.add_item(channel_select)
        
        cancel_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Cancelar",
            custom_id="cancel_channel"
        )
        
        async def cancel_channel_callback(cancel_interaction):
            from .configlogs_preview import create_preview
            preview_data = await create_preview(self.log_type, self.message_config, interaction.guild)
            
            await cancel_interaction.response.edit_message(
                content=f"<:No:825734196256440340> Cambio de canal cancelado.\n{preview_data['content']}",
                embed=preview_data.get("embed"),
                view=self
            )
        
        cancel_btn.callback = cancel_channel_callback
        temp_view.add_item(cancel_btn)
        
        await interaction.response.edit_message(
            content="Selecciona el nuevo canal para los logs:",
            embed=None,
            view=temp_view
        )
    
    async def save_callback(self, interaction: discord.Interaction):
        is_valid = True
        validation_message = ""
        
        if self.message_config.get("embed", False):
            if not self.message_config.get("description", ""):
                is_valid = False
                validation_message = "El embed debe tener una descripción."
        else:
            if not self.message_config.get("message", ""):
                is_valid = False
                validation_message = "Debes configurar un mensaje de texto."
        
        if not is_valid:
            await interaction.response.send_message(
                f"<:No:825734196256440340> {validation_message}",
                ephemeral=True
            )
            return
        
        self.config_data["message"] = self.message_config
        self.config_data["log_channel"] = self.channel_id
        self.config_data["activated"] = True
        
        if self.log_type in ["mod_ch", "mod_cat"]:
            self.config_data["changedname"] = self.message_config.get("changedname", False)
            self.config_data["changedperms"] = self.message_config.get("changedperms", False)
        
        if update_server_data(self.guild_id, f"audit_logs/{self.log_type}", self.config_data):
            channel = interaction.guild.get_channel(self.channel_id)
            
            saved_msg = f"<:Si:825734135116070962> **{LOG_TYPES[self.log_type]['name']}** configurados correctamente:\n\n"
            saved_msg += f"• Canal: {channel.mention if channel else 'No encontrado'}\n"
            saved_msg += f"• Tipo: {'Embed' if self.message_config.get('embed', False) else 'Mensaje normal'}\n"
            
            if self.log_type in ["mod_ch", "mod_cat"]:
                saved_msg += "• Opciones adicionales:\n"
                saved_msg += f"  - Seguimiento de cambios de nombre: {'✅' if self.message_config.get('changedname', False) else '❌'}\n"
                saved_msg += f"  - Seguimiento de cambios de permisos: {'✅' if self.message_config.get('changedperms', False) else '❌'}\n"
            
            await interaction.response.edit_message(
                content=saved_msg,
                embed=None,
                view=None
            )
        else:
            await interaction.response.send_message(
                "<:No:825734196256440340> Error al guardar la configuración. Inténtalo de nuevo.",
                ephemeral=True
            )

class MessageTypeView(discord.ui.View):
    def __init__(self, interaction, guild_id, log_type, config_data):
        super().__init__(timeout=60)
        self.interaction = interaction
        self.guild_id = guild_id
        self.log_type = log_type
        self.config_data = config_data
        self.channel_id = config_data.get("log_channel", 0)
        
        normal_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Mensaje normal",
            custom_id="normal"
        )
        normal_btn.callback = self.normal_callback
        self.add_item(normal_btn)
        
        embed_btn = discord.ui.Button(
            style=discord.ButtonStyle.primary,
            label="Mensaje embed",
            custom_id="embed"
        )
        embed_btn.callback = self.embed_callback
        self.add_item(embed_btn)
        
        cancel_btn = discord.ui.Button(
            style=discord.ButtonStyle.danger,
            label="Cancelar",
            custom_id="cancel_type"
        )
        cancel_btn.callback = self.cancel_callback
        self.add_item(cancel_btn)
    
    async def cancel_callback(self, interaction: discord.Interaction):
        original_view = LogConfigView(self.interaction, self.guild_id, self.log_type, self.config_data)
        
        await interaction.response.edit_message(
            content=f"<:No:825734196256440340> Configuración cancelada para **{LOG_TYPES[self.log_type]['name']}**.",
            embed=None,
            view=original_view
        )
    
    async def normal_callback(self, interaction: discord.Interaction):
        if "message" not in self.config_data or not isinstance(self.config_data["message"], dict):
            self.config_data["message"] = LogMessageModel.create_default()
        
        self.config_data["message"]["embed"] = False
        
        modal = TextMessageModal(self.log_type)
        await interaction.response.send_modal(modal)
    
    async def embed_callback(self, interaction: discord.Interaction):
        if "message" not in self.config_data or not isinstance(self.config_data["message"], dict):
            self.config_data["message"] = LogMessageModel.create_default()
        
        self.config_data["message"]["embed"] = True
        
        modal = EmbedTitleDescriptionModal(self.log_type)
        await interaction.response.send_modal(modal)


class ConfirmView(discord.ui.View):
    def __init__(self, interaction, guild_id, log_type, config_data):
        super().__init__(timeout=60)
        self.interaction = interaction
        self.guild_id = guild_id
        self.log_type = log_type
        self.config_data = config_data
    
    @discord.ui.button(label="Confirmar", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        update_data = {
            "activated": False
        }
        
        if update_server_data(self.guild_id, f"audit_logs/{self.log_type}", update_data):
            await interaction.response.edit_message(
                content=f"<:Si:825734135116070962> **{LOG_TYPES[self.log_type]['name']}** desactivados correctamente.",
                embed=None,
                view=None
            )
        else:
            await interaction.response.send_message(
                "<:No:825734196256440340> Error al desactivar los logs. Inténtalo de nuevo.",
                ephemeral=True
            )
    
    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        original_view = LogConfigView(self.interaction, self.guild_id, self.log_type, self.config_data)
        
        from .configlogs_preview import create_preview
        preview_data = await create_preview(self.log_type, self.config_data.get("message", {}), interaction.guild)
        
        await interaction.response.edit_message(
            content=f"<:No:825734196256440340> Operación cancelada. {LOG_TYPES[self.log_type]['name']} siguen activos.\n\n{preview_data['content']}",
            embed=preview_data.get("embed"),
            view=original_view
        )


class ConfirmImageView(discord.ui.View):
    def __init__(self, image_type, interaction, guild_id, log_type, config_data, message_config):
        super().__init__(timeout=60)
        self.image_type = image_type
        self.interaction = interaction
        self.guild_id = guild_id
        self.log_type = log_type
        self.config_data = config_data
        self.message_config = message_config
    
    @discord.ui.button(label="Confirmar", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if self.image_type == "image":
                self.message_config["image"]["has"] = False
            else:
                self.message_config["thumbnail"]["has"] = False
            
            from .configlogs_preview import create_preview
            preview_data = await create_preview(self.log_type, self.message_config, interaction.guild)
            
            new_view = LogConfigDetailView(
                self.interaction,
                self.guild_id,
                self.log_type,
                self.config_data,
                self.message_config
            )
            
            await interaction.response.edit_message(
                content=f"<:Si:825734135116070962> {self.image_type.capitalize()} desactivado correctamente.\n\n{preview_data['content']}",
                embed=preview_data.get("embed"),
                view=new_view
            )
        except Exception as e:
            print(f"Error al desactivar {self.image_type}: {e}")
            await interaction.response.send_message(
                f"<:No:825734196256440340> Error al desactivar {self.image_type}: {str(e)}.",
                ephemeral=True
            )
    
    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        from .configlogs_preview import create_preview
        preview_data = await create_preview(self.log_type, self.message_config, interaction.guild)
        
        new_view = LogConfigDetailView(
            self.interaction,
            self.guild_id,
            self.log_type,
            self.config_data,
            self.message_config
        )
        
        await interaction.response.edit_message(
            content=f"<:No:825734196256440340> Operación cancelada. {self.image_type.capitalize()} sigue activado.\n\n{preview_data['content']}",
            embed=preview_data.get("embed"),
            view=new_view
        )


class ColorSelectView(discord.ui.View):
    def __init__(self, interaction, guild_id, log_type, config_data, message_config):
        super().__init__(timeout=60)
        self.interaction = interaction
        self.guild_id = guild_id
        self.log_type = log_type
        self.config_data = config_data
        self.message_config = message_config
        
        options = []
        for color_key, color_data in COLORS.items():
            options.append(
                discord.SelectOption(
                    label=color_data[1],
                    value=color_key,
                    emoji=color_data[2],
                    description=f"Color {color_data[1]}"
                )
            )
        
        self.color_select = discord.ui.Select(
            placeholder="Selecciona un color",
            options=options
        )
        self.color_select.callback = self.color_select_callback
        self.add_item(self.color_select)
        
        cancel_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Cancelar",
            custom_id="cancel_color"
        )
        cancel_btn.callback = self.cancel_callback
        self.add_item(cancel_btn)
    
    async def color_select_callback(self, interaction: discord.Interaction):
        color_key = self.color_select.values[0]
        
        self.message_config["color"] = color_key
        
        from .configlogs_preview import create_preview
        preview_data = await create_preview(self.log_type, self.message_config, interaction.guild)
        
        new_view = LogConfigDetailView(
            self.interaction,
            self.guild_id,
            self.log_type,
            self.config_data,
            self.message_config
        )
        
        await interaction.response.edit_message(
            content=f"<:Si:825734135116070962> Color cambiado a {COLORS[color_key][1]} {COLORS[color_key][2]}.\n\n{preview_data['content']}",
            embed=preview_data.get("embed"),
            view=new_view
        )
    
    async def cancel_callback(self, interaction: discord.Interaction):
        from .configlogs_preview import create_preview
        preview_data = await create_preview(self.log_type, self.message_config, interaction.guild)
        
        new_view = LogConfigDetailView(
            self.interaction,
            self.guild_id,
            self.log_type,
            self.config_data,
            self.message_config
        )
        
        await interaction.response.edit_message(
            content=f"<:No:825734196256440340> Cambio de color cancelado.\n\n{preview_data['content']}",
            embed=preview_data.get("embed"),
            view=new_view
        )


class FieldsManagementView(discord.ui.View):
    def __init__(self, interaction, guild_id, log_type, config_data, message_config):
        super().__init__(timeout=120)
        self.interaction = interaction
        self.guild_id = guild_id
        self.log_type = log_type
        self.config_data = config_data
        self.message_config = message_config
        
        self.update_fields_select()
        
        back_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Volver",
            custom_id="back_fields"
        )
        back_btn.callback = self.back_callback
        self.add_item(back_btn)
    
    def update_fields_select(self):
        for item in self.children[:]:
            if isinstance(item, discord.ui.Select):
                self.remove_item(item)
        
        fields = self.message_config.get("fields", {})
        if not fields:
            return
        
        options = []
        for field_id, field_data in sorted(fields.items(), key=lambda x: int(x[0])):
            options.append(
                discord.SelectOption(
                    label=f"Campo {field_id}: {field_data.get('name', '')[:20]}",
                    value=field_id,
                    description=field_data.get("value", "")[:50] + ("..." if len(field_data.get("value", "")) > 50 else "")
                )
            )
        
        if options:
            self.fields_select = discord.ui.Select(
                placeholder="Selecciona un campo",
                options=options
            )
            self.fields_select.callback = self.field_select_callback
            self.add_item(self.fields_select)
    
    async def field_select_callback(self, interaction: discord.Interaction):
        field_id = self.fields_select.values[0]
        field_data = self.message_config["fields"].get(field_id, {})
        
        view = FieldManagementAction(
            self.interaction,
            self.guild_id,
            self.log_type,
            self.config_data,
            field_id,
            self.message_config
        )
        
        await interaction.response.edit_message(
            content=f"**Campo {field_id}**\n"
                    f"**Nombre:** {field_data.get('name', '')}\n"
                    f"**Valor:** {field_data.get('value', '')}\n"
                    f"**Inline:** {'Sí' if field_data.get('inline', False) else 'No'}\n\n"
                    f"¿Qué acción deseas realizar?",
            embed=None,
            view=view
        )
    
    async def back_callback(self, interaction: discord.Interaction):
        from .configlogs_preview import create_preview
        preview_data = await create_preview(self.log_type, self.message_config, interaction.guild)
        
        new_view = LogConfigDetailView(
            self.interaction,
            self.guild_id,
            self.log_type,
            self.config_data,
            self.message_config
        )
        
        await interaction.response.edit_message(
            content=preview_data["content"],
            embed=preview_data.get("embed"),
            view=new_view
        )


class FieldManagementAction(discord.ui.View):
    def __init__(self, interaction, guild_id, log_type, config_data, field_id, message_config):
        super().__init__(timeout=60)
        self.interaction = interaction
        self.guild_id = guild_id
        self.log_type = log_type
        self.config_data = config_data
        self.message_config = message_config
        self.field_id = field_id
        
        edit_btn = discord.ui.Button(
            style=discord.ButtonStyle.primary,
            label="Editar",
            custom_id="edit_field"
        )
        edit_btn.callback = self.edit_callback
        self.add_item(edit_btn)
        
        inline = self.message_config["fields"][field_id].get("inline", False)
        inline_btn = discord.ui.Button(
            style=discord.ButtonStyle.success if inline else discord.ButtonStyle.secondary,
            label="Inline: Sí" if inline else "Inline: No",
            custom_id="toggle_inline"
        )
        inline_btn.callback = self.toggle_inline_callback
        self.add_item(inline_btn)
        
        delete_btn = discord.ui.Button(
            style=discord.ButtonStyle.danger,
            label="Eliminar",
            custom_id="delete_field"
        )
        delete_btn.callback = self.delete_callback
        self.add_item(delete_btn)
        
        back_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Volver",
            custom_id="back_field"
        )
        back_btn.callback = self.back_callback
        self.add_item(back_btn)
    
    async def edit_callback(self, interaction: discord.Interaction):
        field_data = self.message_config["fields"].get(self.field_id, {})
        
        modal = FieldModal(
            self.log_type,
            self.field_id,
            current_name=field_data.get("name", ""),
            current_value=field_data.get("value", ""),
            message_config=self.message_config
        )
        
        await interaction.response.send_modal(modal)
    
    async def toggle_inline_callback(self, interaction: discord.Interaction):
        field_id_str = str(self.field_id)
        
        if not isinstance(self.message_config.get("fields"), dict):
            self.message_config["fields"] = {}
            
        if field_id_str not in self.message_config["fields"]:
            await interaction.response.send_message(
                "<:No:825734196256440340> El campo ya no existe.",
                ephemeral=True
            )
            return
            
        if not isinstance(self.message_config["fields"][field_id_str], dict):
            self.message_config["fields"][field_id_str] = {
                "name": "",
                "value": "",
                "inline": False
            }
        
        current_inline = self.message_config["fields"][field_id_str].get("inline", False)
        self.message_config["fields"][field_id_str]["inline"] = not current_inline
        
        field_data = self.message_config["fields"].get(field_id_str, {})
        
        view = FieldManagementAction(
            self.interaction,
            self.guild_id,
            self.log_type,
            self.config_data,
            self.field_id,
            self.message_config
        )
        
        await interaction.response.edit_message(
            content=f"<:Si:825734135116070962> Propiedad inline cambiada.\n\n"
                    f"**Campo {self.field_id}**\n"
                    f"**Nombre:** {field_data.get('name', '')}\n"
                    f"**Valor:** {field_data.get('value', '')}\n"
                    f"**Inline:** {'Sí' if field_data.get('inline', False) else 'No'}\n\n"
                    f"¿Qué acción deseas realizar?",
            embed=None,
            view=view
        )
    
    async def delete_callback(self, interaction: discord.Interaction):
        LogMessageModel.delete_field(self.message_config, self.field_id)
        
        fields_view = FieldsManagementView(
            self.interaction,
            self.guild_id,
            self.log_type,
            self.config_data,
            self.message_config
        )
        
        await interaction.response.edit_message(
            content=f"<:Si:825734135116070962> Campo eliminado correctamente.\n\n"
                    f"**Gestión de campos para {LOG_TYPES[self.log_type]['name']}**\n"
                    f"Selecciona un campo para editarlo o eliminarlo:",
            embed=None,
            view=fields_view
        )
    
    async def back_callback(self, interaction: discord.Interaction):
        fields_view = FieldsManagementView(
            self.interaction,
            self.guild_id,
            self.log_type,
            self.config_data,
            self.message_config
        )
        
        await interaction.response.edit_message(
            content=f"**Gestión de campos para {LOG_TYPES[self.log_type]['name']}**\n"
                    f"Selecciona un campo para editarlo o eliminarlo:",
            embed=None,
            view=fields_view
        )