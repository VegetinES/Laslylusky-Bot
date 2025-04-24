import discord
from discord.ext import commands

class TicketCreateView(discord.ui.View):
    def __init__(self, bot, ticket_config):
        super().__init__(timeout=300)
        self.bot = bot
        self.ticket_config = ticket_config
        self.step = "ticket_channel"
        self.current_page = 0
        
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
        
        next_button = discord.ui.Button(
            style=discord.ButtonStyle.primary,
            label="Siguiente",
            emoji="➡️",
            custom_id="next_step",
            disabled=True,
            row=1
        )
        next_button.callback = self.next_callback
        self.add_item(next_button)
        
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
        for item in list(self.children):
            if isinstance(item, discord.ui.Select) or (isinstance(item, discord.ui.Button) and item.custom_id in ["prev_page", "next_page"]):
                self.remove_item(item)
        
        channels = []
        if self.step == "ticket_channel":
            placeholder = "Selecciona el canal para los tickets"
            for channel in self.bot.interaction_guild.text_channels:
                channels.append(channel)
        elif self.step == "log_channel":
            placeholder = "Selecciona el canal para los logs de tickets"
            for channel in self.bot.interaction_guild.text_channels:
                channels.append(channel)
        
        total_pages = (len(channels) - 1) // 25 + 1
        start_idx = self.current_page * 25
        end_idx = min(start_idx + 25, len(channels))
        current_channels = channels[start_idx:end_idx]
        
        if total_pages > 1:
            prev_page_btn = discord.ui.Button(
                style=discord.ButtonStyle.secondary,
                label="◀️ Página anterior",
                custom_id="prev_page",
                disabled=self.current_page == 0,
                row=2
            )
            prev_page_btn.callback = self.prev_page_callback
            self.add_item(prev_page_btn)
            
            next_page_btn = discord.ui.Button(
                style=discord.ButtonStyle.secondary,
                label="Página siguiente ▶️",
                custom_id="next_page",
                disabled=self.current_page >= total_pages - 1,
                row=2
            )
            next_page_btn.callback = self.next_page_callback
            self.add_item(next_page_btn)
        
        if current_channels:
            options = []
            for channel in current_channels:
                options.append(
                    discord.SelectOption(
                        label=f"#{channel.name}",
                        value=str(channel.id),
                        description=f"Canal #{channel.name}"
                    )
                )
            
            select = discord.ui.Select(
                placeholder=f"{placeholder} (Página {self.current_page + 1}/{total_pages})",
                options=options,
                custom_id="select_channel",
                row=0
            )
            select.callback = self.channel_select_callback
            self.add_item(select)
    
    async def prev_page_callback(self, interaction: discord.Interaction):
        if self.current_page > 0:
            self.current_page -= 1
            self.add_channel_selector()
            
            title = "Crear Nuevo Ticket"
            description = "Selecciona un canal para los tickets."
            
            if self.step == "log_channel":
                ticket_channel = interaction.guild.get_channel(self.ticket_config["ticket_channel"])
                description = f"Canal para tickets: {ticket_channel.mention}\n\nSelecciona el canal para los logs de tickets:"
            
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title=title,
                    description=description,
                    color=0x3498db
                ),
                view=self
            )
    
    async def next_page_callback(self, interaction: discord.Interaction):
        channels = interaction.guild.text_channels
        total_pages = (len(channels) - 1) // 25 + 1
        
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.add_channel_selector()
            
            title = "Crear Nuevo Ticket"
            description = "Selecciona un canal para los tickets."
            
            if self.step == "log_channel":
                ticket_channel = interaction.guild.get_channel(self.ticket_config["ticket_channel"])
                description = f"Canal para tickets: {ticket_channel.mention}\n\nSelecciona el canal para los logs de tickets:"
            
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title=title,
                    description=description,
                    color=0x3498db
                ),
                view=self
            )
    
    async def channel_select_callback(self, interaction: discord.Interaction):
        channel_id = interaction.data["values"][0]
        channel = interaction.guild.get_channel(int(channel_id))
        
        if not channel:
            await interaction.response.send_message(
                "<:No:825734196256440340> No se encontró el canal seleccionado.",
                ephemeral=True
            )
            return
        
        if self.step == "ticket_channel":
            self.ticket_config["ticket_channel"] = int(channel_id)
            next_button = None
            
            for item in self.children:
                if isinstance(item, discord.ui.Button) and item.custom_id == "next_step":
                    next_button = item
                    break
                    
            if next_button:
                next_button.disabled = False
                
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="Crear Nuevo Ticket",
                    description=f"Canal para tickets seleccionado: {channel.mention}\n\nHaz clic en 'Siguiente' para continuar.",
                    color=0x3498db
                ),
                view=self
            )
        elif self.step == "log_channel":
            self.ticket_config["log_channel"] = int(channel_id)
            
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
    
    async def next_callback(self, interaction: discord.Interaction):
        if self.step == "ticket_channel":
            self.step = "log_channel"
            self.current_page = 0
            
            ticket_channel = interaction.guild.get_channel(self.ticket_config["ticket_channel"])
            
            self.add_channel_selector()
            for item in self.children:
                if isinstance(item, discord.ui.Button) and item.custom_id == "next_step":
                    item.disabled = True
            
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="Crear Nuevo Ticket",
                    description=f"Canal para tickets: {ticket_channel.mention}\n\nSelecciona el canal para los logs de tickets:",
                    color=0x3498db
                ),
                view=self
            )
    
    async def back_callback(self, interaction: discord.Interaction):
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
            self.current_page = 0 
            
            self.add_channel_selector()
            for item in self.children:
                if isinstance(item, discord.ui.Button) and item.custom_id == "next_step":
                    item.disabled = not self.ticket_config.get("ticket_channel")
            
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