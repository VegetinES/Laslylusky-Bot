import discord
from discord.ext import commands

class TicketCreateView(discord.ui.View):
    def __init__(self, bot, ticket_config):
        super().__init__(timeout=300)
        self.bot = bot
        self.ticket_config = ticket_config
        self.step = "ticket_channel"
        
        self.add_channel_selector()
        
        back_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Volver",
            emoji="⬅️",
            custom_id="back_to_manage",
            row=1
        )
        back_button.callback = self.back_callback
        self.add_item(back_button)
        
        cancel_button = discord.ui.Button(
            style=discord.ButtonStyle.danger,
            label="Cancelar",
            emoji="❌",
            custom_id="cancel_create",
            row=1
        )
        cancel_button.callback = self.cancel_callback
        self.add_item(cancel_button)
    
    def add_channel_selector(self):
        if self.step == "ticket_channel":
            placeholder = "Selecciona el canal para los tickets"
        elif self.step == "log_channel":
            placeholder = "Selecciona el canal para los logs"
        
        channel_select = discord.ui.ChannelSelect(
            placeholder=placeholder,
            channel_types=[discord.ChannelType.text],
            custom_id="select_channel",
            row=0
        )
        channel_select.callback = self.channel_select_callback
        self.add_item(channel_select)
    
    async def channel_select_callback(self, interaction: discord.Interaction):
        self.bot.interaction_guild = interaction.guild
        
        channel = interaction.data["values"][0]
        channel_id = int(channel)
        channel = interaction.guild.get_channel(channel_id)
        
        if not channel:
            await interaction.response.send_message(
                "<:No:825734196256440340> No se encontró el canal seleccionado.",
                ephemeral=True
            )
            return
        
        if self.step == "ticket_channel":
            self.ticket_config["ticket_channel"] = channel_id
            self.step = "log_channel"
            
            self.clear_items()
            self.add_channel_selector()
            
            back_button = discord.ui.Button(
                style=discord.ButtonStyle.secondary,
                label="Volver",
                emoji="⬅️",
                custom_id="back_to_manage",
                row=1
            )
            back_button.callback = self.back_callback
            self.add_item(back_button)
            
            cancel_button = discord.ui.Button(
                style=discord.ButtonStyle.danger,
                label="Cancelar",
                emoji="❌",
                custom_id="cancel_create",
                row=1
            )
            cancel_button.callback = self.cancel_callback
            self.add_item(cancel_button)
            
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="Crear Nuevo Ticket",
                    description=f"Canal para tickets: {channel.mention}\n\nSelecciona el canal para los logs de tickets:",
                    color=0x3498db
                ),
                view=self
            )
        elif self.step == "log_channel":
            self.ticket_config["log_channel"] = channel_id
            
            from .edit_view import TicketEditView
            ticket_channel = interaction.guild.get_channel(self.ticket_config["ticket_channel"])
            
            edit_view = TicketEditView(self.bot, self.ticket_config, ticket_channel, channel)
            
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="Configurar Ticket",
                    description=f"Configura el ticket para el canal {ticket_channel.mention}",
                    color=0x3498db
                ),
                view=edit_view
            )
    
    async def back_callback(self, interaction: discord.Interaction):
        self.bot.interaction_guild = interaction.guild
        
        if self.step == "ticket_channel":
            from .manage_view import TicketsManageView
            
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
        elif self.step == "log_channel":
            self.step = "ticket_channel"
            
            self.clear_items()
            self.add_channel_selector()
            
            back_button = discord.ui.Button(
                style=discord.ButtonStyle.secondary,
                label="Volver",
                emoji="⬅️",
                custom_id="back_to_manage",
                row=1
            )
            back_button.callback = self.back_callback
            self.add_item(back_button)
            
            cancel_button = discord.ui.Button(
                style=discord.ButtonStyle.danger,
                label="Cancelar",
                emoji="❌",
                custom_id="cancel_create",
                row=1
            )
            cancel_button.callback = self.cancel_callback
            self.add_item(cancel_button)
            
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="Crear Nuevo Ticket",
                    description="Selecciona un canal para los tickets.",
                    color=0x3498db
                ),
                view=self
            )
    
    async def cancel_callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Configuración Cancelada",
            description="<:No:825734196256440340> Has cancelado la creación del ticket.",
            color=0xe74c3c
        )
        
        await interaction.response.edit_message(
            embed=embed,
            view=None
        )