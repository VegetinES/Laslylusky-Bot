import discord
from ...utils.preview import generate_preview

class MessageBaseView:
    @staticmethod
    def create_default_open_message():
        return {
            "embed": True,
            "title": "Sistema de Tickets",
            "description": "Haz clic en el botón correspondiente para abrir un ticket de soporte.",
            "footer": "",
            "color": "blue",
            "fields": [],
            "image": {
                "url": "",
                "enabled": False
            },
            "thumbnail": {
                "url": "",
                "enabled": False
            },
            "buttons": [
                {
                    "label": "Abrir Ticket",
                    "emoji": "🎫",
                    "style": 3,
                    "name_format": "ticket-{id}"
                }
            ],
            "plain_message": ""
        }
    
    @staticmethod
    def create_default_opened_message():
        return {
            "embed": True,
            "title": "Ticket Abierto",
            "description": "Gracias por abrir un ticket. Un miembro del equipo te atenderá lo antes posible.",
            "footer": "",
            "color": "green",
            "fields": [],
            "image": {
                "url": "",
                "enabled": False
            },
            "thumbnail": {
                "url": "",
                "enabled": False
            },
            "plain_message": ""
        }
    
    @staticmethod
    def setup_initial_options(view):
        view.clear_items()
        
        embed_btn = discord.ui.Button(
            style=discord.ButtonStyle.primary,
            label="Mensaje Embed",
            emoji="🔖",
            custom_id="create_embed",
            row=0
        )
        embed_btn.callback = view.embed_callback
        view.add_item(embed_btn)
        
        text_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Mensaje Normal",
            emoji="📝",
            custom_id="create_text",
            row=0
        )
        text_btn.callback = view.text_callback
        view.add_item(text_btn)
    
    @staticmethod
    def add_common_buttons(view):
        preview_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Vista Previa",
            emoji="👁️",
            custom_id="preview",
            row=4
        )
        preview_btn.callback = view.preview_callback
        view.add_item(preview_btn)
        
        back_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Volver",
            emoji="⬅️",
            custom_id="back_to_edit",
            row=4
        )
        back_btn.callback = view.back_callback
        view.add_item(back_btn)
        
        cancel_btn = discord.ui.Button(
            style=discord.ButtonStyle.danger,
            label="Cancelar",
            emoji="❌",
            custom_id="cancel_message",
            row=4
        )
        cancel_btn.callback = view.cancel_callback
        view.add_item(cancel_btn)
    
    @staticmethod
    async def update_view_with_preview(view, interaction, message_config=None):
        try:
            if message_config:
                view.message_config = message_config
            
            view.clear_items()
            view.add_message_options()
            preview = await generate_preview(view.message_type, view.message_config, interaction.guild)
            
            await interaction.response.edit_message(
                content=preview.get("content"),
                embed=preview.get("embed"),
                view=view
            )
        except Exception as e:
            print(f"Error al actualizar vista: {str(e)}")
            await interaction.followup.send(
                f"<:No:825734196256440340> Error al actualizar vista: {str(e)}",
                ephemeral=True
            )