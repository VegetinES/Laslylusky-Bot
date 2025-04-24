import discord
from discord import app_commands
from .views.main_view import TicketsMainView

async def setup_tickets_config(interaction: discord.Interaction, bot):
    try:
        bot.interaction_guild = interaction.guild
        
        view = TicketsMainView(bot)
        embed = discord.Embed(
            title="Configuración del Sistema de Tickets",
            description="Configura el sistema de tickets para tu servidor",
            color=0x3498db
        )
        
        embed.add_field(
            name="❓ Ayuda",
            value="Muestra información detallada sobre cómo configurar y usar el sistema de tickets.",
            inline=False
        )
        
        embed.add_field(
            name="🎫 Gestionar Tickets",
            value="Configura, modifica o elimina los tickets de tu servidor.",
            inline=False
        )
        
        embed.add_field(
            name="❌ Cancelar",
            value="Cancela la configuración de tickets.",
            inline=False
        )
        
        await interaction.response.send_message(
            embed=embed,
            view=view,
            ephemeral=False
        )
    except Exception as e:
        print(f"Error en setup_tickets_config: {e}")
        await interaction.response.send_message(
            f"<:No:825734196256440340> Ocurrió un error: {str(e)}",
            ephemeral=True
        )