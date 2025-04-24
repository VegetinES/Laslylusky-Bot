import discord
from discord import ui
import re

class EmbedBuilderView(ui.View):
    def __init__(self, original_view):
        super().__init__(timeout=300)
        self.original_view = original_view
        self.add_item(EmbedOptionsDropdown(self))
    
    async def return_to_main(self, interaction):
        try:
            print("Intentando volver al menú principal")
            await self.original_view.update_message(interaction)
        except Exception as e:
            print(f"Error al volver al menú principal: {type(e).__name__}: {e}")
            try:
                await interaction.response.send_message(
                    "Hubo un problema al volver al menú principal. Intenta usar el comando nuevamente.", 
                    ephemeral=True
                )
            except:
                pass

class EmbedOptionsDropdown(ui.Select):
    def __init__(self, view):
        self.embed_view = view
        self.original_view = view.original_view
        
        options = [
            discord.SelectOption(
                label="Añadir autor", 
                description="Añade un autor al embed",
                value="add_author"
            ),
            discord.SelectOption(
                label="Añadir cuerpo", 
                description="Añade título, descripción, URL y color al embed",
                value="add_body"
            ),
            discord.SelectOption(
                label="Eliminar embed", 
                description="Eliminar el embed completamente",
                value="delete_embed"
            ),
            discord.SelectOption(
                label="Volver atrás", 
                description="Volver al menú principal",
                value="back"
            )
        ]
        
        # Actualizar opciones si ya existen elementos
        if self.original_view.embed.author and self.original_view.embed.author.name:
            options[0] = discord.SelectOption(
                label="Modificar autor", 
                description="Modifica el autor del embed",
                value="modify_author"
            )
        
        super().__init__(placeholder="Opciones del embed", options=options)
    
    async def callback(self, interaction: discord.Interaction):
        # Verificar que sea el usuario correcto
        if interaction.user.id != self.original_view.user.id:
            await interaction.response.send_message("No puedes interactuar con este menú.", ephemeral=True)
            return
        
        try:
            print(f"EmbedOptionsDropdown callback - Selected value: {self.values[0]}")
            selected_value = self.values[0]
            
            if selected_value == "add_author" or selected_value == "modify_author":
                modal = AuthorModal(self.embed_view)
                await interaction.response.send_modal(modal)
            
            elif selected_value == "add_body":
                modal = BodyModal(self.embed_view)
                await interaction.response.send_modal(modal)
            
            elif selected_value == "delete_embed":
                confirm_view = ConfirmDeleteEmbedView(self.original_view, self.embed_view)
                await interaction.response.edit_message(
                    content="¿Estás seguro de que deseas eliminar el embed?",
                    embed=None,
                    view=confirm_view
                )
            
            elif selected_value == "back":
                await self.embed_view.return_to_main(interaction)
        except Exception as e:
            print(f"Error en EmbedOptionsDropdown callback: {type(e).__name__}: {e}")
            try:
                await interaction.response.send_message(
                    f"Error al procesar la opción: {type(e).__name__}. Por favor, intenta nuevamente.",
                    ephemeral=True
                )
            except:
                pass

class AuthorModal(ui.Modal, title="Autor del Embed"):
    author_name = ui.TextInput(
        label="Nombre del Autor",
        placeholder="Nombre que aparecerá como autor",
        max_length=256,
        required=True
    )
    
    author_url = ui.TextInput(
        label="URL del Autor",
        placeholder="URL al hacer clic en el nombre (opcional)",
        max_length=256,
        required=False
    )
    
    author_icon = ui.TextInput(
        label="URL del Icono",
        placeholder="URL de la imagen de icono (opcional)",
        max_length=256,
        required=False
    )
    
    def __init__(self, view):
        super().__init__()
        self.embed_view = view
        self.original_view = view.original_view
        
        # Pre-rellenar los campos si ya existen
        if self.original_view.embed.author and self.original_view.embed.author.name:
            self.author_name.default = self.original_view.embed.author.name
        if self.original_view.embed.author and self.original_view.embed.author.url:
            self.author_url.default = self.original_view.embed.author.url
        if self.original_view.embed.author and self.original_view.embed.author.icon_url:
            self.author_icon.default = self.original_view.embed.author.icon_url
    
    async def on_submit(self, interaction: discord.Interaction):
        # Validar URL del autor si se proporciona
        if self.author_url.value and not self.author_url.value.startswith(('http://', 'https://')):
            await interaction.response.send_message("La URL del autor debe comenzar con http:// o https://. Por favor, inténtalo de nuevo.", ephemeral=True)
            return
        
        # Validar URL del icono si se proporciona
        if self.author_icon.value and not self.author_icon.value.startswith(('http://', 'https://')):
            await interaction.response.send_message("La URL del icono debe comenzar con http:// o https://. Por favor, inténtalo de nuevo.", ephemeral=True)
            return
        
        # Actualizar el embed
        self.original_view.embed.set_author(
            name=self.author_name.value,
            url=self.author_url.value if self.author_url.value else discord.Embed.Empty,
            icon_url=self.author_icon.value if self.author_icon.value else discord.Embed.Empty
        )
        
        # Actualizar la opción en el menú desplegable
        for child in self.embed_view.children:
            if isinstance(child, EmbedOptionsDropdown):
                for option in child.options:
                    if option.value == "add_author":
                        option.label = "Modificar autor"
                        option.value = "modify_author"
                        option.description = "Modifica el autor del embed"
                        break
        
        # Mostrar opciones de gestión del autor
        author_manage_view = AuthorManageView(self.original_view, self.embed_view)
        await interaction.response.edit_message(
            content=self.original_view.content,
            embed=self.original_view.embed,
            view=author_manage_view
        )

class BodyModal(ui.Modal, title="Cuerpo del Embed"):
    title = ui.TextInput(
        label="Título",
        placeholder="Título principal del embed",
        max_length=256,
        required=False
    )
    
    description = ui.TextInput(
        label="Descripción",
        style=discord.TextStyle.paragraph,
        placeholder="Contenido principal del embed",
        max_length=4000,
        required=False
    )
    
    url = ui.TextInput(
        label="URL",
        placeholder="URL al hacer clic en el título (opcional)",
        max_length=256,
        required=False
    )
    
    color = ui.TextInput(
        label="Color (HEX)",
        placeholder="Código de color hexadecimal (ej: #FF0000)",
        max_length=7,
        required=False
    )
    
    def __init__(self, view):
        super().__init__()
        self.embed_view = view
        self.original_view = view.original_view
        
        # Pre-rellenar los campos si ya existen
        if self.original_view.embed.title:
            self.title.default = self.original_view.embed.title
        if self.original_view.embed.description:
            self.description.default = self.original_view.embed.description
        if self.original_view.embed.url:
            self.url.default = self.original_view.embed.url
        if self.original_view.embed.color:
            hex_color = f"#{self.original_view.embed.color.value:06x}"
            self.color.default = hex_color
    
    async def on_submit(self, interaction: discord.Interaction):
        # Validar URL si se proporciona
        if self.url.value and not self.url.value.startswith(('http://', 'https://')):
            await interaction.response.send_message("La URL debe comenzar con http:// o https://. Por favor, inténtalo de nuevo.", ephemeral=True)
            return
        
        # Validar color si se proporciona
        if self.color.value:
            hex_pattern = r'^#(?:[0-9a-fA-F]{3}){1,2}$'
            if not re.match(hex_pattern, self.color.value):
                await interaction.response.send_message("El formato del color debe ser hexadecimal (ej: #FF0000). Por favor, inténtalo de nuevo.", ephemeral=True)
                return
            # Convertir color HEX a entero
            color_int = int(self.color.value.lstrip('#'), 16)
            self.original_view.embed.color = discord.Color(color_int)
        
        # Actualizar el embed
        if self.title.value:
            self.original_view.embed.title = self.title.value
        if self.description.value:
            self.original_view.embed.description = self.description.value
        if self.url.value:
            self.original_view.embed.url = self.url.value
        
        # Mostrar opciones de gestión del cuerpo
        body_manage_view = BodyManageView(self.original_view, self.embed_view)
        await interaction.response.edit_message(
            content=self.original_view.content,
            embed=self.original_view.embed,
            view=body_manage_view
        )

class AuthorManageView(ui.View):
    def __init__(self, original_view, embed_view):
        super().__init__(timeout=300)
        self.original_view = original_view
        self.embed_view = embed_view
    
    @ui.button(label="Volver atrás", style=discord.ButtonStyle.secondary)
    async def go_back(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.edit_message(
            content=self.original_view.content,
            embed=self.original_view.embed,
            view=self.embed_view
        )
    
    @ui.button(label="Modificar autor", style=discord.ButtonStyle.primary)
    async def modify_author(self, interaction: discord.Interaction, button: ui.Button):
        modal = AuthorModal(self.embed_view)
        await interaction.response.send_modal(modal)
    
    @ui.button(label="Eliminar autor", style=discord.ButtonStyle.danger)
    async def delete_author(self, interaction: discord.Interaction, button: ui.Button):
        confirm_view = ConfirmDeleteAuthorView(self.original_view, self.embed_view)
        await interaction.response.edit_message(
            content="¿Estás seguro de que deseas eliminar el autor del embed?",
            embed=None,
            view=confirm_view
        )

class BodyManageView(ui.View):
    def __init__(self, original_view, embed_view):
        super().__init__(timeout=300)
        self.original_view = original_view
        self.embed_view = embed_view
    
    @ui.button(label="Volver atrás", style=discord.ButtonStyle.secondary)
    async def go_back(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.edit_message(
            content=self.original_view.content,
            embed=self.original_view.embed,
            view=self.embed_view
        )
    
    @ui.button(label="Modificar cuerpo", style=discord.ButtonStyle.primary)
    async def modify_body(self, interaction: discord.Interaction, button: ui.Button):
        modal = BodyModal(self.embed_view)
        await interaction.response.send_modal(modal)
    
    @ui.button(label="Eliminar cuerpo", style=discord.ButtonStyle.danger)
    async def delete_body(self, interaction: discord.Interaction, button: ui.Button):
        confirm_view = ConfirmDeleteBodyView(self.original_view, self.embed_view)
        await interaction.response.edit_message(
            content="¿Estás seguro de que deseas eliminar el cuerpo del embed?",
            embed=None,
            view=confirm_view
        )

class ConfirmDeleteAuthorView(ui.View):
    def __init__(self, original_view, embed_view):
        super().__init__(timeout=180)
        self.original_view = original_view
        self.embed_view = embed_view
    
    @ui.button(label="Confirmar", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: ui.Button):
        # Eliminar el autor
        self.original_view.embed.remove_author()
        
        # Actualizar las opciones del menú desplegable
        for child in self.embed_view.children:
            if isinstance(child, EmbedOptionsDropdown):
                for option in child.options:
                    if option.value == "modify_author":
                        option.label = "Añadir autor"
                        option.value = "add_author"
                        option.description = "Añade un autor al embed"
                        break
        
        await interaction.response.edit_message(
            content=self.original_view.content,
            embed=self.original_view.embed,
            view=self.embed_view
        )
    
    @ui.button(label="Cancelar", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: ui.Button):
        author_manage_view = AuthorManageView(self.original_view, self.embed_view)
        await interaction.response.edit_message(
            content=self.original_view.content,
            embed=self.original_view.embed,
            view=author_manage_view
        )

class ConfirmDeleteBodyView(ui.View):
    def __init__(self, original_view, embed_view):
        super().__init__(timeout=180)
        self.original_view = original_view
        self.embed_view = embed_view
    
    @ui.button(label="Confirmar", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: ui.Button):
        # Eliminar el cuerpo
        if self.original_view.embed.title:
            self.original_view.embed.title = None
        if self.original_view.embed.description:
            self.original_view.embed.description = None
        if self.original_view.embed.url:
            self.original_view.embed.url = None
        
        # Restablecer el color al azul predeterminado
        self.original_view.embed.color = discord.Color.blue()
        
        await interaction.response.edit_message(
            content=self.original_view.content,
            embed=self.original_view.embed,
            view=self.embed_view
        )
    
    @ui.button(label="Cancelar", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: ui.Button):
        body_manage_view = BodyManageView(self.original_view, self.embed_view)
        await interaction.response.edit_message(
            content=self.original_view.content,
            embed=self.original_view.embed,
            view=body_manage_view
        )

class ConfirmDeleteEmbedView(ui.View):
    def __init__(self, original_view, embed_view):
        super().__init__(timeout=180)
        self.original_view = original_view
        self.embed_view = embed_view
    
    @ui.button(label="Confirmar", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: ui.Button):
        # Eliminar el embed
        self.original_view.embed = None
        
        await self.original_view.update_message(interaction)
    
    @ui.button(label="Cancelar", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.edit_message(
            content=self.original_view.content,
            embed=self.original_view.embed,
            view=self.embed_view
        )