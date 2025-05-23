import discord
from ..embeds import create_ticket_detail_embed, create_ticket_perms_embed, create_ticket_messages_embed
from .perms_view import TicketPermsView
from .messages_view import TicketMessagesView

class TicketDetailView(discord.ui.View):
    def __init__(self, author_id, guild_data, ticket_channel_id):
        super().__init__(timeout=180)
        self.author_id = author_id
        self.guild_data = guild_data
        self.ticket_channel_id = ticket_channel_id

        self.perms_button = discord.ui.Button(
            style=discord.ButtonStyle.primary,
            label="Ver permisos",
            custom_id="perms_ticket"
        )
        self.perms_button.callback = self.perms_callback
        self.add_item(self.perms_button)

        self.messages_button = discord.ui.Button(
            style=discord.ButtonStyle.primary,
            label="Ver mensajes",
            custom_id="messages_ticket"
        )
        self.messages_button.callback = self.messages_callback
        self.add_item(self.messages_button)
        
        self.back_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Volver atrás",
            custom_id="back_ticket"
        )
        self.back_button.callback = self.back_callback
        self.add_item(self.back_button)
        
        self.cancel_button = discord.ui.Button(
            style=discord.ButtonStyle.danger,
            label="Cancelar",
            custom_id="cancel_ticket"
        )
        self.cancel_button.callback = self.cancel_callback
        self.add_item(self.cancel_button)
    
    async def interaction_check(self, interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "Solo la persona que ejecutó el comando puede usar estos controles.",
                ephemeral=True
            )
            return False
        return True
    
    async def perms_callback(self, interaction):
        ticket_config = self.guild_data["tickets"][self.ticket_channel_id]
        embed = await create_ticket_perms_embed(self.ticket_channel_id, ticket_config, interaction)
        view = TicketPermsView(self.author_id, self.guild_data, self.ticket_channel_id)
        
        await interaction.response.edit_message(
            content=None,
            embed=embed,
            view=view
        )
    
    async def messages_callback(self, interaction):
        ticket_config = self.guild_data["tickets"][self.ticket_channel_id]
        embed = await create_ticket_messages_embed(self.ticket_channel_id, ticket_config, interaction)
        view = TicketMessagesView(self.author_id, self.guild_data, self.ticket_channel_id)
        
        await interaction.response.edit_message(
            content=None,
            embed=embed,
            view=view
        )
    
    async def back_callback(self, interaction):
        from .list_view import TicketsListView
        view = TicketsListView(self.author_id, self.guild_data)
        await interaction.response.edit_message(
            content="Selecciona un ticket para ver sus detalles:",
            view=view,
            embed=None
        )
    
    async def cancel_callback(self, interaction):
        for child in self.children:
            child.disabled = True
        
        await interaction.response.edit_message(
            content="Visualización de datos cancelada.",
            view=self,
            embed=None
        )
        self.stop()