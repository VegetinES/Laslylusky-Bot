import discord
from ..embeds import create_ticket_detail_embed
from .detail_view import TicketDetailView

class TicketsListView(discord.ui.View):
    def __init__(self, author_id, guild_data):
        super().__init__(timeout=180)
        self.author_id = author_id
        self.guild_data = guild_data
        self.ticket_data = guild_data.get("tickets", {})
        
        ticket_channels = []
        for channel_id, data in self.ticket_data.items():
            if channel_id.isdigit() and not data.get("__deleted", False):
                channel_name = f"Canal #{channel_id}"
                ticket_channels.append((channel_id, channel_name))
        
        if ticket_channels:
            options = []
            
            for channel_id, channel_name in ticket_channels:
                options.append(
                    discord.SelectOption(
                        label=f"Ticket: {channel_id}",
                        value=channel_id,
                        description=f"Configuración de ticket para canal ID: {channel_id}",
                        emoji="🎫"
                    )
                )

            options.append(
                discord.SelectOption(
                    label="Volver atrás",
                    value="back",
                    description="Volver al menú principal",
                    emoji="⬅️"
                )
            )
            options.append(
                discord.SelectOption(
                    label="Cancelar",
                    value="cancel",
                    description="Cancelar visualización",
                    emoji="❌"
                )
            )
            
            self.tickets_select = discord.ui.Select(
                placeholder="Selecciona un ticket",
                options=options
            )
            self.tickets_select.callback = self.tickets_select_callback
            self.add_item(self.tickets_select)
        else:
            self.back_button = discord.ui.Button(
                style=discord.ButtonStyle.secondary,
                label="Volver atrás",
                custom_id="back_tickets"
            )
            self.back_button.callback = self.back_callback
            self.add_item(self.back_button)
            
            self.cancel_button = discord.ui.Button(
                style=discord.ButtonStyle.danger,
                label="Cancelar",
                custom_id="cancel_tickets"
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
    
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        
        try:
            await self.message.edit(view=self)
        except:
            pass
    
    async def back_callback(self, interaction):
        from ....configdata import ConfigDataMainView
        view = ConfigDataMainView(self.author_id, self.guild_data, interaction)
        await interaction.response.edit_message(
            content="Selecciona qué información quieres ver:",
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
    
    async def tickets_select_callback(self, interaction):
        selection = self.tickets_select.values[0]
        
        if selection == "back":
            await self.back_callback(interaction)
        elif selection == "cancel":
            await self.cancel_callback(interaction)
        else:
            ticket_config = self.ticket_data[selection]
            embed = await create_ticket_detail_embed(selection, ticket_config, interaction)
            view = TicketDetailView(self.author_id, self.guild_data, selection)
            
            await interaction.response.edit_message(
                content=None,
                embed=embed,
                view=view
            )