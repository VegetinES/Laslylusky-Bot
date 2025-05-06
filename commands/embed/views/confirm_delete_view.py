import discord
from discord import ui
from .main_view import EmbedMainView

class ConfirmDeleteView(ui.View):
    def __init__(self, main_view):
        super().__init__(timeout=1800)
        self.main_view = main_view
    
    @ui.button(label="Confirmar", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: ui.Button):
        self.main_view.content = None
        self.main_view.embeds = []
        self.main_view.view_data = None
        
        new_main_view = EmbedMainView(self.main_view.bot, self.main_view.user, self.main_view.embed_cache)
        
        await interaction.response.edit_message(
            content=None,
            embed=discord.Embed(
                description="Todo el contenido ha sido eliminado. Puedes comenzar de nuevo.",
                color=discord.Color.blue()
            ),
            view=new_main_view
        )
    
    @ui.button(label="Cancelar", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: ui.Button):
        await self.main_view.update_message(interaction)

class ConfirmDeleteContentView(ui.View):
    def __init__(self, main_view):
        super().__init__(timeout=1800)
        self.main_view = main_view
    
    @ui.button(label="Confirmar", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: ui.Button):
        self.main_view.content = None
        await self.main_view.update_message(interaction)
    
    @ui.button(label="Cancelar", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: ui.Button):
        from .content_view import ContentView
        content_view = ContentView(self.main_view)
        await content_view.show(interaction)

class ConfirmDeleteEmbedView(ui.View):
    def __init__(self, main_view, embed_index):
        super().__init__(timeout=1800)
        self.main_view = main_view
        self.embed_index = embed_index
    
    @ui.button(label="Confirmar", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: ui.Button):
        self.main_view.remove_embed(self.embed_index)
        
        from .embeds_views import EmbedsView
        embeds_view = EmbedsView(self.main_view)
        await embeds_view.show(interaction)
    
    @ui.button(label="Cancelar", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: ui.Button):
        from .embed_edit_view import EmbedEditView
        edit_view = EmbedEditView(self.main_view, self.embed_index)
        await edit_view.show(interaction)