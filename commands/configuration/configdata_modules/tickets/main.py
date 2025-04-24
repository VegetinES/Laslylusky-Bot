import discord
import traceback
from .views import TicketsListView

async def show_tickets_data(interaction, guild_data, author_id):
    try:
        ticket_data = guild_data.get("tickets", {})
        valid_tickets = False
        
        for channel_id, data in ticket_data.items():
            if channel_id.isdigit() and not data.get("__deleted", False):
                valid_tickets = True
                break
        
        view = TicketsListView(author_id, guild_data)
        
        if valid_tickets:
            await interaction.response.edit_message(
                content="Selecciona un ticket para ver sus detalles:",
                view=view,
                embed=None
            )
        else:
            await interaction.response.edit_message(
                content="No hay tickets configurados en este servidor.",
                view=view,
                embed=None
            )
    except Exception as e:
        print(f"Error en show_tickets_data: {e}")
        traceback.print_exc()
        await interaction.response.send_message(
            f"Error al mostrar los datos de tickets: {e}",
            ephemeral=True
        )