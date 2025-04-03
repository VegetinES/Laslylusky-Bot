import discord
from database.update import update_server_data
from .configlogs_constants import (
    MAX_NORMAL_MESSAGE, MAX_EMBED_TITLE, MAX_EMBED_DESCRIPTION, 
    MAX_EMBED_FOOTER, MAX_FIELD_NAME, MAX_FIELD_VALUE, validate_message_params
)
from .configlogs_models import LogMessageModel

class TextMessageModal(discord.ui.Modal):
    def __init__(self, log_type, current_message="", title="Configurar mensaje de texto", message_config=None):
        super().__init__(title=title)
        self.log_type = log_type
        self.message_config = message_config if message_config is not None else LogMessageModel.create_default()
        
        self.message = discord.ui.TextInput(
            label="Mensaje de texto",
            style=discord.TextStyle.paragraph,
            placeholder="Escribe el mensaje de texto usando los parámetros disponibles",
            default=current_message,
            required=True,
            max_length=MAX_NORMAL_MESSAGE
        )
        
        self.add_item(self.message)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            guild_id = interaction.guild.id
            log_type = self.log_type
            
            from database.get import get_specific_field
            audit_logs = get_specific_field(guild_id, "audit_logs")
            if audit_logs and log_type in audit_logs:
                config_data = audit_logs[log_type]
            else:
                await interaction.followup.send(
                    "<:No:825734196256440340> No se encontró la configuración de logs.",
                    ephemeral=True
                )
                return

            self.message_config["embed"] = False
            self.message_config["message"] = self.message.value
            
            from .configlogs_preview import create_preview
            preview_data = await create_preview(log_type, self.message_config, interaction.guild)
            
            from .configlogs_views import LogConfigDetailView
            new_view = LogConfigDetailView(
                interaction, 
                guild_id, 
                log_type, 
                config_data,
                self.message_config
            )
            
            await interaction.followup.edit_message(
                message_id=interaction.message.id,
                content=preview_data["content"],
                embed=preview_data.get("embed"),
                view=new_view
            )
            
            await interaction.followup.send(
                "<:Si:825734135116070962> Mensaje de texto configurado correctamente.",
                ephemeral=True
            )
            
        except Exception as e:
            print(f"Error al actualizar mensaje de texto: {e}")
            await interaction.followup.send(
                f"<:No:825734196256440340> Error al actualizar el mensaje: {str(e)}. Por favor, intenta de nuevo.",
                ephemeral=True
            )


class EmbedTitleDescriptionModal(discord.ui.Modal):
    def __init__(self, log_type, current_title="", current_description="", title="Configurar título y descripción", message_config=None):
        super().__init__(title=title)
        self.log_type = log_type
        self.message_config = message_config if message_config is not None else LogMessageModel.create_default()
        
        self.embed_title = discord.ui.TextInput(
            label="Título del embed (opcional)",
            style=discord.TextStyle.short,
            placeholder="Título del embed",
            default=current_title,
            required=False,
            max_length=MAX_EMBED_TITLE
        )
        
        self.embed_description = discord.ui.TextInput(
            label="Descripción del embed (obligatorio)",
            style=discord.TextStyle.paragraph,
            placeholder="Descripción del embed usando los parámetros disponibles",
            default=current_description,
            required=True,
            max_length=MAX_EMBED_DESCRIPTION
        )
        
        self.add_item(self.embed_title)
        self.add_item(self.embed_description)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            guild_id = interaction.guild.id
            log_type = self.log_type
            
            from database.get import get_specific_field
            audit_logs = get_specific_field(guild_id, "audit_logs")
            if audit_logs and log_type in audit_logs:
                config_data = audit_logs[log_type]
            else:
                await interaction.followup.send(
                    "<:No:825734196256440340> No se encontró la configuración de logs.",
                    ephemeral=True
                )
                return

            self.message_config["title"] = self.embed_title.value
            self.message_config["description"] = self.embed_description.value
            self.message_config["embed"] = True
            
            from .configlogs_preview import create_preview
            preview_data = await create_preview(log_type, self.message_config, interaction.guild)
            
            from .configlogs_views import LogConfigDetailView
            new_view = LogConfigDetailView(
                interaction, 
                guild_id, 
                log_type, 
                config_data,
                self.message_config
            )
            
            await interaction.followup.edit_message(
                message_id=interaction.message.id,
                content=preview_data["content"],
                embed=preview_data.get("embed"),
                view=new_view
            )
            
            await interaction.followup.send(
                "<:Si:825734135116070962> Título y descripción configurados correctamente.",
                ephemeral=True
            )
            
        except Exception as e:
            print(f"Error al actualizar título y descripción: {e}")
            await interaction.followup.send(
                f"<:No:825734196256440340> Error al actualizar el mensaje: {str(e)}. Por favor, intenta de nuevo.",
                ephemeral=True
            )


class EmbedFooterModal(discord.ui.Modal):
    def __init__(self, log_type, current_footer="", title="Configurar footer", message_config=None):
        super().__init__(title=title)
        self.log_type = log_type
        self.message_config = message_config if message_config is not None else LogMessageModel.create_default()
        
        self.embed_footer = discord.ui.TextInput(
            label="Footer del embed (opcional)",
            style=discord.TextStyle.short,
            placeholder="Footer del embed",
            default=current_footer,
            required=False,
            max_length=MAX_EMBED_FOOTER
        )
        
        self.add_item(self.embed_footer)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            guild_id = interaction.guild.id
            log_type = self.log_type
            
            from database.get import get_specific_field
            audit_logs = get_specific_field(guild_id, "audit_logs")
            if not audit_logs or log_type not in audit_logs:
                await interaction.followup.send(
                    "<:No:825734196256440340> No se encontró la configuración de logs.",
                    ephemeral=True
                )
                return
            
            config_data = audit_logs[log_type]
            
            self.message_config["footer"] = self.embed_footer.value
            self.message_config["embed"] = True
            
            from .configlogs_preview import create_preview
            preview_data = await create_preview(log_type, self.message_config, interaction.guild)
            
            from .configlogs_views import LogConfigDetailView
            new_view = LogConfigDetailView(
                interaction, 
                guild_id, 
                log_type, 
                config_data,
                self.message_config
            )
            
            await interaction.followup.edit_message(
                message_id=interaction.message.id,
                content=preview_data["content"],
                embed=preview_data.get("embed"),
                view=new_view
            )
            
            await interaction.followup.send(
                "<:Si:825734135116070962> Footer configurado correctamente.",
                ephemeral=True
            )
            
        except Exception as e:
            print(f"Error al actualizar footer: {e}")
            await interaction.followup.send(
                f"<:No:825734196256440340> Error al actualizar el footer: {str(e)}. Por favor, intenta de nuevo.",
                ephemeral=True
            )


class FieldModal(discord.ui.Modal):
    def __init__(self, log_type, field_id, current_name="", current_value="", title="Configurar campo", message_config=None):
        super().__init__(title=title)
        self.log_type = log_type
        self.field_id = field_id
        self.message_config = message_config if message_config is not None else LogMessageModel.create_default()
        
        self.field_name = discord.ui.TextInput(
            label="Nombre del campo",
            style=discord.TextStyle.short,
            placeholder="Nombre del campo",
            default=current_name,
            required=True,
            max_length=MAX_FIELD_NAME
        )
        
        self.field_value = discord.ui.TextInput(
            label="Valor del campo",
            style=discord.TextStyle.paragraph,
            placeholder="Valor del campo",
            default=current_value,
            required=True,
            max_length=MAX_FIELD_VALUE
        )
        
        self.add_item(self.field_name)
        self.add_item(self.field_value)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            guild_id = interaction.guild.id
            log_type = self.log_type
            
            from database.get import get_specific_field
            audit_logs = get_specific_field(guild_id, "audit_logs")
            if not audit_logs or log_type not in audit_logs:
                await interaction.followup.send(
                    "<:No:825734196256440340> No se encontró la configuración de logs.",
                    ephemeral=True
                )
                return
            
            config_data = audit_logs[log_type]
            
            success, message = LogMessageModel.update_field(
                self.message_config, 
                str(self.field_id),
                self.field_name.value, 
                self.field_value.value,
                None
            )
            
            if not success:
                await interaction.followup.send(
                    f"<:No:825734196256440340> {message}",
                    ephemeral=True
                )
                return
            
            from .configlogs_preview import create_preview
            preview_data = await create_preview(log_type, self.message_config, interaction.guild)
            
            from .configlogs_views import LogConfigDetailView
            new_view = LogConfigDetailView(
                interaction, 
                guild_id, 
                log_type, 
                config_data,
                self.message_config
            )
            
            await interaction.followup.edit_message(
                message_id=interaction.message.id,
                content=preview_data["content"],
                embed=preview_data.get("embed"),
                view=new_view
            )
            
            await interaction.followup.send(
                f"<:Si:825734135116070962> Campo actualizado correctamente.",
                ephemeral=True
            )
            
        except Exception as e:
            print(f"Error al actualizar campo: {e}")
            await interaction.followup.send(
                f"<:No:825734196256440340> Error al actualizar el campo: {str(e)}. Por favor, intenta de nuevo.",
                ephemeral=True
            )


class ImageParamModal(discord.ui.Modal):
    def __init__(self, log_type, image_type, current_param="", title="Configurar imagen", message_config=None):
        super().__init__(title=title)
        self.log_type = log_type
        self.image_type = image_type
        self.message_config = message_config if message_config is not None else LogMessageModel.create_default()
        
        self.image_param = discord.ui.TextInput(
            label=f"Parámetro de {image_type}",
            style=discord.TextStyle.short,
            placeholder="URL o {servericon} o {useravatar}",
            default=current_param,
            required=True,
        )
        
        self.add_item(self.image_param)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            guild_id = interaction.guild.id
            log_type = self.log_type
            
            from database.get import get_specific_field
            audit_logs = get_specific_field(guild_id, "audit_logs")
            
            if not audit_logs or log_type not in audit_logs:
                await interaction.followup.send(
                    "<:No:825734196256440340> No se encontró la configuración de logs.",
                    ephemeral=True
                )
                return
            
            config_data = audit_logs[log_type]
            
            if not LogMessageModel.validate_image_param(self.image_param.value):
                await interaction.followup.send(
                    "<:No:825734196256440340> El parámetro de imagen no es válido. Debe ser una URL válida o uno de los siguientes parámetros: {servericon}, {useravatar}",
                    ephemeral=True
                )
                return
            
            if self.image_type == "image":
                self.message_config["image"]["has"] = True
                self.message_config["image"]["param"] = self.image_param.value
            else:
                self.message_config["thumbnail"]["has"] = True
                self.message_config["thumbnail"]["param"] = self.image_param.value
            
            from .configlogs_preview import create_preview
            preview_data = await create_preview(log_type, self.message_config, interaction.guild)
            
            from .configlogs_views import LogConfigDetailView
            new_view = LogConfigDetailView(
                interaction, 
                guild_id, 
                log_type, 
                config_data,
                self.message_config
            )
            
            await interaction.followup.edit_message(
                message_id=interaction.message.id,
                content=preview_data["content"],
                embed=preview_data.get("embed"),
                view=new_view
            )
            
            await interaction.followup.send(
                f"<:Si:825734135116070962> {self.image_type} configurado correctamente.",
                ephemeral=True
            )
            
        except Exception as e:
            print(f"Error al actualizar imagen: {e}")
            await interaction.followup.send(
                f"<:No:825734196256440340> Error al actualizar la imagen: {str(e)}. Por favor, intenta de nuevo.",
                ephemeral=True
            )