import discord
from discord import ui
from ..constants import MAX_CONTENT_LENGTH

class ContentView(ui.View):
    def __init__(self, main_view):
        super().__init__(timeout=1800)
        self.main_view = main_view
    
    async def show(self, interaction):
        if not self.main_view.content:
            modal = ContentModal(self.main_view)
            await interaction.response.send_modal(modal)
        else:
            preview_embed = discord.Embed(
                title="Gestión de Contenido",
                description=f"Contenido actual:\n```{self.main_view.content[:500]}{'...' if len(self.main_view.content) > 500 else ''}```",
                color=discord.Color.blue()
            )
            await interaction.response.edit_message(embed=preview_embed, view=self)
    
    @ui.button(label="Volver atrás", style=discord.ButtonStyle.secondary)
    async def go_back(self, interaction: discord.Interaction, button: ui.Button):
        await self.main_view.update_message(interaction)
    
    @ui.button(label="Modificar contenido", style=discord.ButtonStyle.primary)
    async def modify_content(self, interaction: discord.Interaction, button: ui.Button):
        modal = ContentModal(self.main_view)
        await interaction.response.send_modal(modal)
    
    @ui.button(label="Eliminar contenido", style=discord.ButtonStyle.danger)
    async def delete_content(self, interaction: discord.Interaction, button: ui.Button):
        from .confirm_delete_view import ConfirmDeleteContentView
        confirm_view = ConfirmDeleteContentView(self.main_view)
        await interaction.response.edit_message(
            content="¿Estás seguro de que deseas eliminar el contenido?",
            embed=None,
            view=confirm_view
        )

class ContentModal(ui.Modal, title="Contenido del Mensaje"):
    content = ui.TextInput(
        label="Contenido",
        style=discord.TextStyle.paragraph,
        placeholder="Escribe el contenido del mensaje aquí...",
        max_length=MAX_CONTENT_LENGTH,
        required=False
    )
    
    def __init__(self, main_view):
        super().__init__()
        self.main_view = main_view
        if main_view.content:
            self.content.default = main_view.content
    
    async def on_submit(self, interaction: discord.Interaction):
        self.main_view.content = self.content.value if self.content.value else None
        await self.main_view.update_message(interaction)