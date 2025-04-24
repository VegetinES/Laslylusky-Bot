import discord
from discord import ui

class ContentView(ui.View):
    def __init__(self, original_view):
        super().__init__(timeout=300)
        self.original_view = original_view
    
    @ui.button(label="Volver atrás", style=discord.ButtonStyle.secondary)
    async def go_back(self, interaction: discord.Interaction, button: ui.Button):
        await self.original_view.update_message(interaction)
    
    @ui.button(label="Modificar contenido", style=discord.ButtonStyle.primary)
    async def modify_content(self, interaction: discord.Interaction, button: ui.Button):
        modal = ContentModifyModal(self.original_view)
        await interaction.response.send_modal(modal)
    
    @ui.button(label="Eliminar mensaje normal", style=discord.ButtonStyle.danger)
    async def delete_content(self, interaction: discord.Interaction, button: ui.Button):
        confirm_view = ConfirmDeleteContentView(self.original_view)
        await interaction.response.edit_message(
            content="¿Estás seguro de que deseas eliminar el contenido del mensaje?",
            embed=None,
            view=confirm_view
        )

class ContentModifyModal(ui.Modal, title="Modificar Contenido"):
    content = ui.TextInput(
        label="Contenido",
        style=discord.TextStyle.paragraph,
        placeholder="Escribe el contenido del mensaje aquí...",
        max_length=2000,
        required=False
    )
    
    def __init__(self, view):
        super().__init__()
        self.main_view = view
        # Pre-rellenar el campo con el contenido actual
        if view.content:
            self.content.default = view.content
    
    async def on_submit(self, interaction: discord.Interaction):
        self.main_view.content = self.content.value
        
        # Actualizar la vista previa
        content_view = ContentView(self.main_view)
        preview_embed = discord.Embed(
            description="Contenido actualizado del mensaje",
            color=discord.Color.blue()
        )
        await interaction.response.edit_message(content=self.main_view.content, embed=preview_embed, view=content_view)

class ConfirmDeleteContentView(ui.View):
    def __init__(self, original_view):
        super().__init__(timeout=180)
        self.original_view = original_view
    
    @ui.button(label="Confirmar", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: ui.Button):
        # Eliminar el contenido
        self.original_view.content = None
        
        # Actualizar las opciones del menú desplegable
        for child in self.original_view.children:
            if isinstance(child, discord.ui.Select):
                for option in child.options:
                    if option.value == "manage_content":
                        option.label = "Añadir contenido del mensaje"
                        option.value = "add_content"
                        option.description = "Añade un mensaje de texto normal"
                        break
        
        await interaction.response.edit_message(
            content=None,
            embed=discord.Embed(
                description="El contenido del mensaje ha sido eliminado.",
                color=discord.Color.blue()
            ),
            view=self.original_view
        )
    
    @ui.button(label="Cancelar", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: ui.Button):
        content_view = ContentView(self.original_view)
        preview_embed = discord.Embed(
            description="Contenido actual del mensaje",
            color=discord.Color.blue()
        )
        await interaction.response.edit_message(content=self.original_view.content, embed=preview_embed, view=content_view)