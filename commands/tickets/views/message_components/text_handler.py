import discord
from ...utils.modals import MessageTextModal
from .message_base_view import MessageBaseView

class TextHandlerView:
    @staticmethod
    def setup_text_options(view):
        edit_text_btn = discord.ui.Button(
            style=discord.ButtonStyle.primary,
            label="Editar Mensaje",
            emoji="📝",
            custom_id="edit_text",
            row=0
        )
        edit_text_btn.callback = view.edit_text_callback
        view.add_item(edit_text_btn)
        
        add_embed_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Añadir Embed",
            emoji="🔖",
            custom_id="add_embed",
            row=1
        )
        add_embed_btn.callback = view.add_embed_callback
        view.add_item(add_embed_btn)
    
    @staticmethod
    def add_text_button(view):
        add_text_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Añadir Mensaje Normal",
            emoji="📝",
            custom_id="add_text",
            row=3
        )
        add_text_btn.callback = view.add_text_callback
        view.add_item(add_text_btn)
    
    @staticmethod
    def add_remove_text_button(view):
        remove_text_btn = discord.ui.Button(
            style=discord.ButtonStyle.danger,
            label="Quitar Mensaje Normal",
            emoji="🗑️",
            custom_id="remove_text",
            row=3
        )
        remove_text_btn.callback = view.remove_text_callback
        view.add_item(remove_text_btn)
    
    @staticmethod
    async def handle_text_creation(view, interaction):
        view.message_config["embed"] = False
        
        modal = MessageTextModal()
        await interaction.response.send_modal(modal)
        
        modal.callback = lambda i, message: TextHandlerView.update_text_message(view, i, message)
    
    @staticmethod
    async def update_text_message(view, interaction, message):
        view.message_config["plain_message"] = message
        
        await MessageBaseView.update_view_with_preview(view, interaction)
    
    @staticmethod
    async def handle_add_text(view, interaction):
        modal = MessageTextModal()
        await interaction.response.send_modal(modal)
        
        modal.callback = lambda i, message: TextHandlerView.update_plain_message(view, i, message)
    
    @staticmethod
    async def update_plain_message(view, interaction, message):
        view.message_config["plain_message"] = message
        
        await MessageBaseView.update_view_with_preview(view, interaction)
    
    @staticmethod
    async def handle_remove_text(view, interaction):
        view.message_config["plain_message"] = ""
        
        await MessageBaseView.update_view_with_preview(view, interaction)
    
    @staticmethod
    async def handle_edit_text(view, interaction):
        modal = MessageTextModal(view.message_config.get("plain_message", ""))
        await interaction.response.send_modal(modal)
        
        modal.callback = lambda i, message: TextHandlerView.update_plain_message(view, i, message)