import discord
from discord.ext import commands
from ..utils.database import get_tickets_data
from ..constants import DEFAULT_TICKET_CONFIG

class TicketsManageView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot
        self.current_page = 0
        self.add_ticket_selector()
        
        create_button = discord.ui.Button(
            style=discord.ButtonStyle.success,
            label="Crear Nuevo Ticket",
            emoji="➕",
            custom_id="create_ticket",
            row=1
        )
        create_button.callback = self.create_ticket_callback
        self.add_item(create_button)
        
        back_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Volver",
            emoji="⬅️",
            custom_id="back_to_main",
            row=2
        )
        back_button.callback = self.back_callback
        self.add_item(back_button)
        
        cancel_button = discord.ui.Button(
            style=discord.ButtonStyle.danger,
            label="Cancelar",
            emoji="❌",
            custom_id="cancel_manage",
            row=2
        )
        cancel_button.callback = self.cancel_callback
        self.add_item(cancel_button)
    
    def add_ticket_selector(self):
        from ..utils.database import get_tickets_data
        
        for item in list(self.children):
            if isinstance(item, discord.ui.Select) or (isinstance(item, discord.ui.Button) and item.custom_id in ["prev_page", "next_page"]):
                self.remove_item(item)
        
        options = []
        tickets_data = {}
        
        if hasattr(self.bot, 'interaction_guild') and self.bot.interaction_guild:
            guild_id = self.bot.interaction_guild.id
            tickets_data = get_tickets_data(guild_id)
        
        ticket_options = []
        if tickets_data and len(tickets_data) > 0:
            for channel_id, ticket_data in tickets_data.items():
                channel = None
                if hasattr(self.bot, 'interaction_guild'):
                    channel = self.bot.interaction_guild.get_channel(int(channel_id))
                if channel:
                    ticket_options.append({
                        "label": f"Ticket en #{channel.name}",
                        "value": channel_id,
                        "description": f"Configuración de ticket en #{channel.name}",
                        "emoji": "🎫"
                    })

        total_pages = (len(ticket_options) - 1) // 25 + 1
        start_idx = self.current_page * 25
        end_idx = min(start_idx + 25, len(ticket_options))
        current_options = ticket_options[start_idx:end_idx]
        
        if total_pages > 1:
            prev_page_btn = discord.ui.Button(
                style=discord.ButtonStyle.secondary,
                label="◀️ Página anterior",
                custom_id="prev_page",
                disabled=self.current_page == 0,
                row=3
            )
            prev_page_btn.callback = self.prev_page_callback
            self.add_item(prev_page_btn)
            
            next_page_btn = discord.ui.Button(
                style=discord.ButtonStyle.secondary,
                label="Página siguiente ▶️", 
                custom_id="next_page",
                disabled=self.current_page >= total_pages - 1,
                row=3
            )
            next_page_btn.callback = self.next_page_callback
            self.add_item(next_page_btn)
        
        if current_options:
            options = [discord.SelectOption(
                label=opt["label"],
                value=opt["value"],
                description=opt["description"],
                emoji=opt["emoji"]
            ) for opt in current_options]
            
            select = discord.ui.Select(
                placeholder=f"Selecciona un ticket para modificar (Página {self.current_page + 1}/{max(1, total_pages)})",
                options=options,
                custom_id="select_ticket",
                row=0
            )
            select.callback = self.ticket_select_callback
            self.add_item(select)
    
    async def prev_page_callback(self, interaction: discord.Interaction):
        if self.current_page > 0:
            self.current_page -= 1
            self.bot.interaction_guild = interaction.guild
            self.add_ticket_selector()
            
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="Gestión de Tickets",
                    description="Selecciona un ticket existente para modificarlo o crea uno nuevo.",
                    color=0x3498db
                ),
                view=self
            )
    
    async def next_page_callback(self, interaction: discord.Interaction):
        from ..utils.database import get_tickets_data
        
        self.bot.interaction_guild = interaction.guild
        tickets_data = get_tickets_data(interaction.guild.id)
        total_pages = (len(tickets_data) - 1) // 25 + 1
        
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.add_ticket_selector()
            
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="Gestión de Tickets",
                    description="Selecciona un ticket existente para modificarlo o crea uno nuevo.",
                    color=0x3498db
                ),
                view=self
            )
    
    async def ticket_select_callback(self, interaction: discord.Interaction):
        self.bot.interaction_guild = interaction.guild
        channel_id = interaction.data["values"][0]
        
        from .edit_view import TicketEditView
        from ..utils.database import get_ticket_data
        
        ticket_data = get_ticket_data(interaction.guild.id, channel_id)
        if not ticket_data:
            await interaction.response.send_message(
                "<:No:825734196256440340> No se encontró la configuración del ticket.",
                ephemeral=True
            )
            return
        
        ticket_channel = interaction.guild.get_channel(int(channel_id))
        log_channel = interaction.guild.get_channel(int(ticket_data.get("log_channel", 0) or 0))
        
        edit_view = TicketEditView(self.bot, ticket_data, ticket_channel, log_channel)
        
        embed = discord.Embed(
            title=f"Editar Ticket en #{ticket_channel.name if ticket_channel else 'Canal Desconocido'}",
            description="Modifica la configuración de este ticket.",
            color=0x3498db
        )
        
        await interaction.response.edit_message(
            embed=embed,
            view=edit_view
        )
    
    async def create_ticket_callback(self, interaction: discord.Interaction):
        from .create_view import TicketCreateView
        from ..constants import DEFAULT_TICKET_CONFIG
        
        self.bot.interaction_guild = interaction.guild
        
        ticket_config = {}
        
        for key, value in DEFAULT_TICKET_CONFIG.items():
            if isinstance(value, dict):
                if key == "permissions":
                    ticket_config[key] = {
                        "manage": {
                            "roles": [],
                            "users": []
                        },
                        "view": {
                            "roles": [],
                            "users": []
                        }
                    }
                elif key == "open_message":
                    ticket_config[key] = {
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
                                "id": "default",
                                "label": "Abrir Ticket",
                                "emoji": "🎫",
                                "style": 3,
                                "name_format": "ticket-{id}",
                                "description": "Abrir un ticket de soporte general"
                            }
                        ],
                        "plain_message": ""
                    }
                elif key == "opened_messages":
                    ticket_config[key] = {
                        "default": {
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
                    }
                else:
                    ticket_config[key] = {}
            else:
                ticket_config[key] = value
        
        ticket_config["ticket_channel"] = None
        ticket_config["log_channel"] = None
        ticket_config["auto_increment"] = {}
        
        view = TicketCreateView(self.bot, ticket_config)
        embed = discord.Embed(
            title="Crear Nuevo Ticket",
            description="Selecciona un canal para los tickets.",
            color=0x3498db
        )
        
        await interaction.response.edit_message(
            embed=embed,
            view=view
        )
    
    async def back_callback(self, interaction: discord.Interaction):
        from .main_view import TicketsMainView
        
        self.bot.interaction_guild = interaction.guild
        
        view = TicketsMainView(self.bot)
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