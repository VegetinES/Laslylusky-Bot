import discord
from datetime import datetime

class TicketsListView(discord.ui.View):
    def __init__(self, author_id, guild_data):
        super().__init__(timeout=180)
        self.author_id = author_id
        self.guild_data = guild_data
        self.ticket_data = guild_data.get("tickets", {})
        
        ticket_channels = []
        for channel_id, data in self.ticket_data.items():
            if channel_id.isdigit() and not data.get("_removed", False):
                ticket_channels.append((channel_id, data.get("tickets-name", "Ticket")))
        
        if ticket_channels:
            options = []
            
            for channel_id, ticket_name in ticket_channels:
                options.append(
                    discord.SelectOption(
                        label=f"Ticket: {ticket_name}",
                        value=channel_id,
                        description=f"ID del canal: {channel_id}",
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
        from .configdata import ConfigDataMainView
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
    
    async def back_callback(self, interaction):
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

class TicketPermsView(discord.ui.View):
    def __init__(self, author_id, guild_data, ticket_channel_id):
        super().__init__(timeout=180)
        self.author_id = author_id
        self.guild_data = guild_data
        self.ticket_channel_id = ticket_channel_id
        
        self.details_button = discord.ui.Button(
            style=discord.ButtonStyle.primary,
            label="Ver detalles",
            custom_id="details_ticket"
        )
        self.details_button.callback = self.details_callback
        self.add_item(self.details_button)

        self.back_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Volver atrás",
            custom_id="back_ticket_perms"
        )
        self.back_button.callback = self.back_callback
        self.add_item(self.back_button)
        
        self.cancel_button = discord.ui.Button(
            style=discord.ButtonStyle.danger,
            label="Cancelar",
            custom_id="cancel_ticket_perms"
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
    
    async def details_callback(self, interaction):
        ticket_config = self.guild_data["tickets"][self.ticket_channel_id]
        embed = await create_ticket_detail_embed(self.ticket_channel_id, ticket_config, interaction)
        view = TicketDetailView(self.author_id, self.guild_data, self.ticket_channel_id)
        
        await interaction.response.edit_message(
            content=None,
            embed=embed,
            view=view
        )
    
    async def back_callback(self, interaction):
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

def format_list(id_list, get_entity, default="ninguno"):
    if not id_list or id_list == [0]:
        return default
            
    entity_mentions = []
    for eid in id_list:
        if eid != 0:
            entity = get_entity(eid)
            if entity:
                entity_mentions.append(f"{entity.mention} `[ID: {entity.id}]`")
        
    return "\n".join(entity_mentions) if entity_mentions else default

async def create_ticket_detail_embed(channel_id, ticket_config, interaction):
    embed = discord.Embed(
        title="Detalles de configuración de tickets",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    
    channel = interaction.guild.get_channel(int(channel_id))
    
    ticket_name = ticket_config.get("tickets-name", "Ticket-{id}")
    current_id = ticket_config.get("id", 1)
    log_channel_id = ticket_config.get("log-channel")
    log_channel = interaction.guild.get_channel(log_channel_id) if log_channel_id else None
    setup_stage = ticket_config.get("setup_stage", 0)

    setup_status = {
        0: "⚠️ No configurado",
        1: "⚠️ Canal configurado (faltan permisos)",
        2: "⚠️ Permisos configurados (faltan mensajes)",
        3: "✅ Completamente configurado"
    }.get(setup_stage, "⚠️ Estado desconocido")
    
    embed.add_field(
        name="Información general",
        value=(
            f"🎫 **Canal:** {channel.mention if channel else 'No encontrado'} (`{channel_id}`)\n"
            f"📝 **Nombre tickets:** `{ticket_name}`\n"
            f"🔢 **ID actual:** `{current_id}`\n"
            f"📋 **Logs:** {log_channel.mention if log_channel else 'No configurado'}\n"
            f"⚙️ **Estado:** {setup_status}\n"
        ),
        inline=False
    )

    ticket_abrir = ticket_config.get("ticket-abrir", False)
    embed.add_field(
        name="Botón para abrir tickets",
        value="✅ Configurado" if ticket_abrir else "❌ No configurado",
        inline=False
    )
    
    ticket_abierto = ticket_config.get("ticket-abierto", {})
    is_activated = ticket_abierto.get("activado", False)
    embed.add_field(
        name="Mensaje para tickets abiertos",
        value="✅ Configurado" if is_activated else "❌ No configurado",
        inline=False
    )

    if ticket_abrir:
        embed.add_field(
            name="Vista previa de botón para abrir tickets",
            value="Información detallada sobre el mensaje para abrir tickets",
            inline=False
        )

    if is_activated:
        title = ticket_abierto.get("title", "Ticket Abierto")
        description = ticket_abierto.get("descripcion", "Un miembro del staff te atenderá pronto.")
        footer = ticket_abierto.get("footer", None)
        
        embed.add_field(
            name="Vista previa de mensaje para tickets abiertos",
            value=(
                f"**Título:** {title}\n"
                f"**Descripción:** {description}\n"
                f"**Footer:** {footer if footer else 'No configurado'}"
            ),
            inline=False
        )
    
    embed.set_footer(text=f"Solicitado por {interaction.user.name}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
    return embed

async def create_ticket_perms_embed(channel_id, ticket_config, interaction):
    embed = discord.Embed(
        title="Permisos de tickets",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    
    channel = interaction.guild.get_channel(int(channel_id))
    
    embed.add_field(
        name="Canal de tickets",
        value=f"{channel.mention if channel else 'No encontrado'} (`{channel_id}`)",
        inline=False
    )
    
    perms_config = ticket_config.get("perms", {})
    
    perm_types = {
        "manage": ("Gestionar tickets", "manage-roles", "manage-users"),
        "see": ("Ver tickets", "see-roles", "see-users"),
        "close": ("Cerrar tickets", "close-roles", "close-users"),
        "add-del-usr": ("Añadir/eliminar usuarios", "add-del-usr-roles", "add-del-usr-users")
    }
    
    for perm_key, (perm_name, roles_key, users_key) in perm_types.items():
        roles_list = perms_config.get(roles_key, [0])
        users_list = perms_config.get(users_key, [0])
        
        roles_text = format_list(
            roles_list, 
            lambda rid: interaction.guild.get_role(rid)
        )
        
        users_text = format_list(
            users_list,
            lambda uid: interaction.guild.get_member(uid)
        )
        
        embed.add_field(
            name=f"**{perm_name}**",
            value=f"**Roles:**\n{roles_text}\n\n**Usuarios:**\n{users_text}",
            inline=False
        )
    
    embed.set_footer(text=f"Solicitado por {interaction.user.name}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
    return embed

async def show_tickets_data(interaction, guild_data, author_id):
    try:
        ticket_data = guild_data.get("tickets", {})
        valid_tickets = False
        
        for channel_id, data in ticket_data.items():
            if channel_id.isdigit() and not data.get("_removed", False):
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
                content="No hay tickets activados/configurados en este servidor.",
                view=view,
                embed=None
            )
    except Exception as e:
        print(f"Error en show_tickets_data: {e}")
        await interaction.response.send_message(
            f"Error al mostrar los datos de tickets: {e}",
            ephemeral=True
        )