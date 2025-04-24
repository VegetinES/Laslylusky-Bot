import discord
from discord.ext import commands
from ..utils.helpers import show_tickets_help

class TicketsMainView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot
        
        help_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Ayuda",
            emoji="❓",
            custom_id="tickets_help",
            row=0
        )
        help_button.callback = self.help_callback
        self.add_item(help_button)
        
        manage_button = discord.ui.Button(
            style=discord.ButtonStyle.primary,
            label="Gestionar Tickets",
            emoji="🎫",
            custom_id="tickets_manage",
            row=0
        )
        manage_button.callback = self.manage_callback
        self.add_item(manage_button)
        
        cancel_button = discord.ui.Button(
            style=discord.ButtonStyle.danger,
            label="Cancelar",
            emoji="❌",
            custom_id="tickets_cancel",
            row=0
        )
        cancel_button.callback = self.cancel_callback
        self.add_item(cancel_button)
    
    async def help_callback(self, interaction: discord.Interaction):
        self.bot.interaction_guild = interaction.guild
        await show_tickets_help(interaction)
    
    async def manage_callback(self, interaction: discord.Interaction):
        from .manage_view import TicketsManageView
        
        self.bot.interaction_guild = interaction.guild
        
        view = TicketsManageView(self.bot)
        embed = discord.Embed(
            title="Gestión de Tickets",
            description="Selecciona un ticket existente para modificarlo o crea uno nuevo.",
            color=0x3498db
        )
        
        await interaction.response.edit_message(
            embed=embed,
            view=view
        )
    
    async def cancel_callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Configuración Cancelada",
            description="<:No:825734196256440340> Has cancelado la configuración del sistema de tickets.",
            color=0xe74c3c
        )
        
        await interaction.response.edit_message(
            embed=embed,
            view=None
        )