import discord
from discord import ui
from ..constants import (
    MAX_TITLE_LENGTH, MAX_DESCRIPTION_LENGTH, MAX_FIELD_NAME_LENGTH,
    MAX_FIELD_VALUE_LENGTH, MAX_AUTHOR_NAME_LENGTH, MAX_FOOTER_TEXT_LENGTH
)

class EmbedBasicModal(ui.Modal, title="Editar información básica"):
    def __init__(self, edit_view):
        super().__init__(title="Editar información básica")
        self.edit_view = edit_view
        self.embed = edit_view.embed
        
        self.title_input = ui.TextInput(
            label="Título",
            style=discord.TextStyle.short,
            placeholder="Título del embed",
            max_length=256,
            required=False,
            default=self.embed.title if self.embed.title else ""
        )
        
        self.description_input = ui.TextInput(
            label="Descripción",
            style=discord.TextStyle.paragraph,
            placeholder="Descripción del embed",
            max_length=4000,
            required=False,
            default=self.embed.description if self.embed.description else ""
        )
        
        self.url_input = ui.TextInput(
            label="URL",
            style=discord.TextStyle.short,
            placeholder="URL del embed (https://...)",
            max_length=256,
            required=False,
            default=self.embed.url if self.embed.url else ""
        )
        
        self.add_item(self.title_input)
        self.add_item(self.description_input)
        self.add_item(self.url_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            print(f"EmbedBasicModal.on_submit: Procesando formulario")
            
            title_value = self.title_input.value.strip()
            description_value = self.description_input.value.strip()
            url_value = self.url_input.value.strip()
            
            if title_value:
                self.embed.title = title_value
            else:
                self.embed.title = None 
            
            if description_value:
                self.embed.description = description_value
            else:
                self.embed.description = None

            if url_value:
                self.embed.url = url_value
            else:
                self.embed.url = None
            
            if not title_value and not description_value and not url_value:
                if self.embed.fields or self.embed.image or self.embed.thumbnail:
                    self.embed.title = None
                    self.embed.description = None
                    self.embed.url = None
                    
                    await self.edit_view.show(interaction)
                    print("EmbedBasicModal.on_submit: Campos title, description y url eliminados")
                    return
                else:
                    await self.edit_view.show(interaction)
                    print("EmbedBasicModal.on_submit: No hay cambios (todos los campos vacíos)")
                    return
            
            self.embed.title = title_value or None
            self.embed.description = description_value or None
            self.embed.url = url_value or None
            
            await self.edit_view.show(interaction)
            print("EmbedBasicModal.on_submit: Embed actualizado correctamente")
            
        except Exception as e:
            print(f"EmbedBasicModal.on_submit: Error: {e}")
            await interaction.followup.send(
                f"Error al procesar el formulario: {str(e)}",
                ephemeral=True
            )

class EmbedAuthorModal(ui.Modal, title="Gestionar autor"):
    author_name = ui.TextInput(
        label="Nombre del autor",
        style=discord.TextStyle.short,
        placeholder="Nombre del autor",
        max_length=MAX_AUTHOR_NAME_LENGTH,
        required=False
    )
    
    author_url = ui.TextInput(
        label="URL del autor",
        style=discord.TextStyle.short,
        placeholder="URL al hacer clic en el nombre",
        required=False
    )
    
    author_icon = ui.TextInput(
        label="URL del icono",
        style=discord.TextStyle.short,
        placeholder="URL de la imagen del autor",
        required=False
    )
    
    def __init__(self, edit_view):
        super().__init__()
        self.edit_view = edit_view
        self.embed = edit_view.embed
        
        if self.embed.author:
            if self.embed.author.name:
                self.author_name.default = self.embed.author.name
            if self.embed.author.url:
                self.author_url.default = self.embed.author.url
            if self.embed.author.icon_url:
                self.author_icon.default = self.embed.author.icon_url
    
    async def on_submit(self, interaction: discord.Interaction):
        author_name = self.author_name.value
        author_url = self.author_url.value
        author_icon = self.author_icon.value
        
        if author_url and not author_url.startswith(('http://', 'https://')):
            await interaction.response.send_message("La URL del autor debe comenzar con http:// o https://", ephemeral=True)
            return
        
        if author_icon and not author_icon.startswith(('http://', 'https://')):
            await interaction.response.send_message("La URL del icono debe comenzar con http:// o https://", ephemeral=True)
            return
        
        if author_name or author_url or author_icon:
            self.embed.set_author(
                name=author_name or None,
                url=author_url or None,
                icon_url=author_icon or None
            )
        else:
            self.embed.remove_author()
        
        await self.edit_view.show(interaction)

class EmbedFieldModal(ui.Modal, title="Editar campo"):
    field_name = ui.TextInput(
        label="Nombre del campo",
        style=discord.TextStyle.short,
        placeholder="Nombre del campo",
        max_length=MAX_FIELD_NAME_LENGTH,
        required=True
    )
    
    field_value = ui.TextInput(
        label="Valor del campo",
        style=discord.TextStyle.paragraph,
        placeholder="Valor del campo",
        max_length=MAX_FIELD_VALUE_LENGTH,
        required=True
    )
    
    field_inline = ui.TextInput(
        label="Inline (si/no)",
        style=discord.TextStyle.short,
        placeholder="si/no",
        max_length=2,
        required=False
    )
    
    def __init__(self, edit_view, field_index):
        super().__init__()
        self.edit_view = edit_view
        self.embed = edit_view.embed
        self.field_index = field_index
        
        if field_index >= 0 and field_index < len(self.embed.fields):
            field = self.embed.fields[field_index]
            self.field_name.default = field.name
            self.field_value.default = field.value
            self.field_inline.default = "si" if field.inline else "no"
    
    async def on_submit(self, interaction: discord.Interaction):
        inline = self.field_inline.value.lower() in ['si', 's', 'yes', 'y']
        
        if self.field_index >= 0 and self.field_index < len(self.embed.fields):
            self.embed.set_field_at(
                self.field_index,
                name=self.field_name.value,
                value=self.field_value.value,
                inline=inline
            )
        else:
            self.embed.add_field(
                name=self.field_name.value,
                value=self.field_value.value,
                inline=inline
            )
        
        from ..views.fields_view import FieldsView
        fields_view = FieldsView(self.edit_view)
        await fields_view.show(interaction)

class EmbedImageModal(ui.Modal, title="Gestionar imágenes"):
    image_url = ui.TextInput(
        label="URL de la imagen",
        style=discord.TextStyle.paragraph,
        placeholder="URL de la imagen principal",
        required=False,
        max_length=2000
    )
    
    thumbnail_url = ui.TextInput(
        label="URL del thumbnail",
        style=discord.TextStyle.paragraph,
        placeholder="URL de la imagen pequeña",
        required=False,
        max_length=2000
    )
    
    def __init__(self, edit_view):
        super().__init__()
        self.edit_view = edit_view
        self.embed = edit_view.embed
        
        if self.embed.image:
            self.image_url.default = self.embed.image.url
        if self.embed.thumbnail:
            self.thumbnail_url.default = self.embed.thumbnail.url
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            image_url = self.image_url.value.strip() if self.image_url.value else ""
            thumbnail_url = self.thumbnail_url.value.strip() if self.thumbnail_url.value else ""
            
            if image_url and not (image_url.startswith('http://') or image_url.startswith('https://')):
                await interaction.response.send_message("La URL de la imagen debe comenzar con http:// o https://", ephemeral=True)
                return
            
            if thumbnail_url and not (thumbnail_url.startswith('http://') or thumbnail_url.startswith('https://')):
                await interaction.response.send_message("La URL del thumbnail debe comenzar con http:// o https://", ephemeral=True)
                return
            
            if image_url:
                self.embed.set_image(url=image_url)
            else:
                self.embed.set_image(url=None)
            
            if thumbnail_url:
                self.embed.set_thumbnail(url=thumbnail_url)
            else:
                self.embed.set_thumbnail(url=None)
            
            await self.edit_view.show(interaction)
            
        except Exception as e:
            print(f"Error inesperado en EmbedImageModal.on_submit: {type(e).__name__} - {e}")
            await interaction.followup.send(
                f"Error inesperado: {type(e).__name__} - {e}. Por favor, intenta de nuevo con otra URL.",
                ephemeral=True
            )

class EmbedColorModal(ui.Modal, title="Editar color"):
    color = ui.TextInput(
        label="Color (hex)",
        style=discord.TextStyle.short,
        placeholder="#FF0000",
        max_length=7,
        required=False
    )
    
    def __init__(self, edit_view):
        super().__init__()
        self.edit_view = edit_view
        self.embed = edit_view.embed
        
        if self.embed.color:
            hex_color = f"#{self.embed.color.value:06x}"
            self.color.default = hex_color
    
    async def on_submit(self, interaction: discord.Interaction):
        color_value = self.color.value
        
        if color_value:
            if not color_value.startswith('#'):
                color_value = '#' + color_value
            
            try:
                color_int = int(color_value.lstrip('#'), 16)
                self.embed.color = discord.Color(color_int)
            except ValueError:
                await interaction.response.send_message("Formato de color inválido. Usa formato hexadecimal (ej: #FF0000)", ephemeral=True)
                return
        else:
            self.embed.color = None
        
        await self.edit_view.show(interaction)

class EmbedFooterModal(ui.Modal, title="Editar footer"):
    footer_text = ui.TextInput(
        label="Texto del footer",
        style=discord.TextStyle.short,
        placeholder="Texto del footer",
        max_length=MAX_FOOTER_TEXT_LENGTH,
        required=False
    )
    
    footer_icon = ui.TextInput(
        label="URL del icono",
        style=discord.TextStyle.short,
        placeholder="URL de la imagen del footer",
        required=False
    )
    
    timestamp = ui.TextInput(
        label="Timestamp (si/no)",
        style=discord.TextStyle.short,
        placeholder="si/no",
        max_length=2,
        required=False
    )
    
    def __init__(self, edit_view):
        super().__init__()
        self.edit_view = edit_view
        self.embed = edit_view.embed
        
        if self.embed.footer:
            if self.embed.footer.text:
                self.footer_text.default = self.embed.footer.text
            if self.embed.footer.icon_url:
                self.footer_icon.default = self.embed.footer.icon_url
        
        self.timestamp.default = "si" if self.embed.timestamp else "no"
    
    async def on_submit(self, interaction: discord.Interaction):
        footer_text = self.footer_text.value
        footer_icon = self.footer_icon.value
        
        if footer_icon and not footer_icon.startswith(('http://', 'https://')):
            await interaction.response.send_message("La URL del icono debe comenzar con http:// o https://", ephemeral=True)
            return
        
        if footer_text or footer_icon:
            self.embed.set_footer(
                text=footer_text or None,
                icon_url=footer_icon or None
            )
        else:
            self.embed.set_footer(text=discord.Embed.Empty)
        
        use_timestamp = self.timestamp.value.lower() in ['si', 's', 'yes', 'y']
        if use_timestamp:
            self.embed.timestamp = discord.utils.utcnow()
        else:
            self.embed.timestamp = None
        
        await self.edit_view.show(interaction)