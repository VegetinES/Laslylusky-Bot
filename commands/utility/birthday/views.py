import discord
import re
import math
from discord import ui
from .utils import parse_timezone, get_user_timezone

class ConfigView(ui.View):
    def __init__(self, bot, db, config=None):
        super().__init__(timeout=300)
        self.bot = bot
        self.db = db
        self.config = config or {}
        self.temp_config = {
            "channel_id": self.config.get("channel_id"),
            "message": self.config.get("message", "¡Feliz cumpleaños [@users]! 🎂🎉"),
            "timezone": self.config.get("timezone", "UTC+00:00"),
            "guild_id": None
        }
    
    @ui.button(label="Establecer canal de felicitaciones", style=discord.ButtonStyle.primary, row=0)
    async def set_channel(self, interaction: discord.Interaction, button: ui.Button):
        self.temp_config["guild_id"] = interaction.guild.id
        
        channels = [ch for ch in interaction.guild.text_channels]
        view = ChannelSelectView(self.bot, self.db, self.temp_config, channels)
        
        await interaction.response.edit_message(
            content="Selecciona el canal donde se enviarán las felicitaciones de cumpleaños:",
            embed=None,
            view=view
        )
    
    @ui.button(label="Establecer mensaje", style=discord.ButtonStyle.primary, row=0)
    async def set_message(self, interaction: discord.Interaction, button: ui.Button):
        self.temp_config["guild_id"] = interaction.guild.id
        
        view = MessageView(self.bot, self.db, self.temp_config)
        embed = discord.Embed(
            title="Mensaje de Felicitación",
            description="Configura el mensaje que se enviará en los cumpleaños.\n\n"
                       "Usa `[@users]` para mencionar a los usuarios que cumplen años:\n"
                       "- Si es una persona: @usuario\n"
                       "- Si son varias: @usuario1, @usuario2 y @usuario3",
            color=discord.Color.blue()
        )
        
        await interaction.response.edit_message(
            content=None,
            embed=embed,
            view=view
        )
    
    @ui.button(label="Establecer zona horaria", style=discord.ButtonStyle.primary, row=0)
    async def set_timezone(self, interaction: discord.Interaction, button: ui.Button):
        self.temp_config["guild_id"] = interaction.guild.id
        
        view = TimeZoneView(self.bot, self.db, self.temp_config)
        embed = discord.Embed(
            title="Zona Horaria",
            description="Configura la zona horaria para el envío de felicitaciones.\n\n"
                       "Formato: ±HH:MM (ejemplos: +01:00, -03:30, +05:45)\n\n"
                       "Los mensajes se enviarán a las 00:00 en esta zona horaria.\n"
                       "Consulta tu zona horaria aquí: https://greenwichmeantime.com/time-zone/",
            color=discord.Color.blue()
        )
        
        await interaction.response.edit_message(
            content=None,
            embed=embed,
            view=view
        )
    
    @ui.button(label="Guardar cambios", style=discord.ButtonStyle.success, row=1)
    async def save_changes(self, interaction: discord.Interaction, button: ui.Button):
        self.temp_config["guild_id"] = interaction.guild.id
        
        if not self.temp_config.get("channel_id"):
            await interaction.response.send_message(
                "<:No:825734196256440340> Debes configurar un canal para las felicitaciones.",
                ephemeral=True
            )
            return
        
        success = await self.db.save_config(self.temp_config)
        
        if success:
            channel = interaction.guild.get_channel(self.temp_config["channel_id"])
            
            embed = discord.Embed(
                title="Configuración Guardada",
                description="La configuración de cumpleaños ha sido guardada correctamente.",
                color=discord.Color.green()
            )
            
            embed.add_field(
                name="Canal de felicitaciones",
                value=channel.mention if channel else "No configurado",
                inline=False
            )
            
            embed.add_field(
                name="Mensaje de felicitación",
                value=self.temp_config.get("message", "No configurado"),
                inline=False
            )
            
            embed.add_field(
                name="Zona horaria",
                value=self.temp_config.get("timezone", "UTC+00:00"),
                inline=False
            )
            
            await interaction.response.edit_message(
                content=None,
                embed=embed,
                view=None
            )
        else:
            await interaction.response.send_message(
                "<:No:825734196256440340> Error al guardar la configuración.",
                ephemeral=True
            )
    
    @ui.button(label="Eliminar configuración", style=discord.ButtonStyle.danger, row=1, disabled=True)
    async def delete_config(self, interaction: discord.Interaction, button: ui.Button):
        if not self.config:
            await interaction.response.send_message(
                "<:No:825734196256440340> No hay configuración para eliminar.",
                ephemeral=True
            )
            return
        
        view = ConfirmDeleteConfigView(self.bot, self.db, interaction.guild.id)
        await interaction.response.edit_message(
            content="¿Estás seguro de que quieres eliminar la configuración de cumpleaños?",
            embed=None,
            view=view
        )

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

class ChannelSelectView(ui.View):
    def __init__(self, bot, db, config, channels, page=0):
        super().__init__(timeout=300)
        self.bot = bot
        self.db = db
        self.config = config
        self.channels = channels
        self.page = page
        self.page_size = 25
        self.max_pages = math.ceil(len(channels) / self.page_size)
        
        self.update_view()
    
    def update_view(self):
        self.clear_items()
        
        start_idx = self.page * self.page_size
        end_idx = min(start_idx + self.page_size, len(self.channels))
        current_channels = self.channels[start_idx:end_idx]
        
        if current_channels:
            options = []
            for channel in current_channels:
                options.append(discord.SelectOption(
                    label=f"#{channel.name}",
                    value=str(channel.id),
                    description=f"Canal #{channel.name}"
                ))
            
            select = ui.Select(
                placeholder=f"Selecciona un canal (Página {self.page+1}/{max(1, self.max_pages)})",
                options=options
            )
            select.callback = self.channel_select_callback
            self.add_item(select)
        
        if self.max_pages > 1:
            prev_button = ui.Button(
                style=discord.ButtonStyle.secondary,
                label="Anterior",
                disabled=self.page == 0
            )
            prev_button.callback = self.previous_page
            self.add_item(prev_button)
            
            next_button = ui.Button(
                style=discord.ButtonStyle.secondary,
                label="Siguiente",
                disabled=self.page >= self.max_pages - 1
            )
            next_button.callback = self.next_page
            self.add_item(next_button)
        
        back_button = ui.Button(
            style=discord.ButtonStyle.primary,
            label="Volver atrás"
        )
        back_button.callback = self.go_back
        self.add_item(back_button)
    
    async def channel_select_callback(self, interaction: discord.Interaction):
        channel_id = int(interaction.data["values"][0])
        channel = interaction.guild.get_channel(channel_id)
        
        if not channel:
            await interaction.response.send_message(
                "<:No:825734196256440340> El canal seleccionado no se encuentra.",
                ephemeral=True
            )
            return
        
        self.config["channel_id"] = channel_id
        
        view = ConfigView(self.bot, self.db, self.config)
        view.temp_config = self.config
        
        for item in view.children:
            if item.label == "Eliminar configuración":
                item.disabled = False
        
        embed = discord.Embed(
            title="Configuración de Cumpleaños",
            description="Configura cómo se manejarán los mensajes de cumpleaños en el servidor.",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="Canal de felicitaciones",
            value=channel.mention,
            inline=False
        )
        
        embed.add_field(
            name="Mensaje de felicitación",
            value=self.config.get("message", "¡Feliz cumpleaños [@users]! 🎂🎉"),
            inline=False
        )
        
        embed.add_field(
            name="Zona horaria",
            value=self.config.get("timezone", "UTC+00:00"),
            inline=False
        )
        
        await interaction.response.edit_message(
            content=None,
            embed=embed,
            view=view
        )
    
    async def previous_page(self, interaction: discord.Interaction):
        self.page = max(0, self.page - 1)
        self.update_view()
        await interaction.response.edit_message(view=self)
    
    async def next_page(self, interaction: discord.Interaction):
        self.page = min(self.max_pages - 1, self.page + 1)
        self.update_view()
        await interaction.response.edit_message(view=self)
    
    async def go_back(self, interaction: discord.Interaction):
        view = ConfigView(self.bot, self.db, self.config)
        view.temp_config = self.config
        
        embed = discord.Embed(
            title="Configuración de Cumpleaños",
            description="Configura cómo se manejarán los mensajes de cumpleaños en el servidor.",
            color=discord.Color.blue()
        )
        
        channel = interaction.guild.get_channel(self.config.get("channel_id")) if self.config.get("channel_id") else None
        channel_text = f"{channel.mention}" if channel else "No configurado"
        
        embed.add_field(
            name="Canal de felicitaciones",
            value=channel_text,
            inline=False
        )
        
        embed.add_field(
            name="Mensaje de felicitación",
            value=self.config.get("message", "¡Feliz cumpleaños [@users]! 🎂🎉"),
            inline=False
        )
        
        embed.add_field(
            name="Zona horaria",
            value=self.config.get("timezone", "UTC+00:00"),
            inline=False
        )
        
        await interaction.response.edit_message(
            content=None,
            embed=embed,
            view=view
        )

class MessageView(ui.View):
    def __init__(self, bot, db, config):
        super().__init__(timeout=300)
        self.bot = bot
        self.db = db
        self.config = config
    
    @ui.button(label="Editar mensaje", style=discord.ButtonStyle.primary)
    async def edit_message(self, interaction: discord.Interaction, button: ui.Button):
        modal = MessageModal(self.config.get("message", "¡Feliz cumpleaños [@users]! 🎂🎉"))
        
        async def modal_callback(interaction, message):
            self.config["message"] = message
            await self.return_to_config(interaction)
        
        modal.callback = modal_callback
        await interaction.response.send_modal(modal)
    
    @ui.button(label="Volver atrás", style=discord.ButtonStyle.secondary)
    async def go_back(self, interaction: discord.Interaction, button: ui.Button):
        await self.return_to_config(interaction)
    
    async def return_to_config(self, interaction):
        view = ConfigView(self.bot, self.db, self.config)
        view.temp_config = self.config
        
        embed = discord.Embed(
            title="Configuración de Cumpleaños",
            description="Configura cómo se manejarán los mensajes de cumpleaños en el servidor.",
            color=discord.Color.blue()
        )
        
        channel = interaction.guild.get_channel(self.config.get("channel_id")) if self.config.get("channel_id") else None
        channel_text = f"{channel.mention}" if channel else "No configurado"
        
        embed.add_field(
            name="Canal de felicitaciones",
            value=channel_text,
            inline=False
        )
        
        embed.add_field(
            name="Mensaje de felicitación",
            value=self.config.get("message", "¡Feliz cumpleaños [@users]! 🎂🎉"),
            inline=False
        )
        
        embed.add_field(
            name="Zona horaria",
            value=self.config.get("timezone", "UTC+00:00"),
            inline=False
        )
        
        await interaction.response.edit_message(
            content=None,
            embed=embed,
            view=view
        )

class TimeZoneView(ui.View):
    def __init__(self, bot, db, config):
        super().__init__(timeout=300)
        self.bot = bot
        self.db = db
        self.config = config
    
    @ui.button(label="Editar zona horaria", style=discord.ButtonStyle.primary)
    async def edit_timezone(self, interaction: discord.Interaction, button: ui.Button):
        modal = TimeZoneModal(self.config.get("timezone", "UTC+00:00"))
        
        async def modal_callback(interaction, timezone):
            self.config["timezone"] = timezone
            await self.return_to_config(interaction)
        
        modal.callback = modal_callback
        await interaction.response.send_modal(modal)
    
    @ui.button(label="Volver atrás", style=discord.ButtonStyle.secondary)
    async def go_back(self, interaction: discord.Interaction, button: ui.Button):
        await self.return_to_config(interaction)
    
    async def return_to_config(self, interaction):
        view = ConfigView(self.bot, self.db, self.config)
        view.temp_config = self.config
        
        embed = discord.Embed(
            title="Configuración de Cumpleaños",
            description="Configura cómo se manejarán los mensajes de cumpleaños en el servidor.",
            color=discord.Color.blue()
        )
        
        channel = interaction.guild.get_channel(self.config.get("channel_id")) if self.config.get("channel_id") else None
        channel_text = f"{channel.mention}" if channel else "No configurado"
        
        embed.add_field(
            name="Canal de felicitaciones",
            value=channel_text,
            inline=False
        )
        
        embed.add_field(
            name="Mensaje de felicitación",
            value=self.config.get("message", "¡Feliz cumpleaños [@users]! 🎂🎉"),
            inline=False
        )
        
        embed.add_field(
            name="Zona horaria",
            value=self.config.get("timezone", "UTC+00:00"),
            inline=False
        )
        
        await interaction.response.edit_message(
            content=None,
            embed=embed,
            view=view
        )

class MessageModal(ui.Modal, title="Mensaje de Felicitación"):
    message = ui.TextInput(
        label="Mensaje",
        style=discord.TextStyle.paragraph,
        placeholder="¡Feliz cumpleaños [@users]! 🎂🎉",
        required=True,
        max_length=1000
    )
    
    def __init__(self, current_message):
        super().__init__()
        self.message.default = current_message
        self.callback = None
    
    async def on_submit(self, interaction: discord.Interaction):
        if self.callback:
            await self.callback(interaction, self.message.value)
        else:
            await interaction.response.send_message(
                "Mensaje configurado.",
                ephemeral=True
            )

class TimeZoneModal(ui.Modal, title="Zona Horaria"):
    timezone = ui.TextInput(
        label="Zona Horaria",
        style=discord.TextStyle.short,
        placeholder="+00:00",
        required=True,
        max_length=6
    )
    
    def __init__(self, current_timezone):
        super().__init__()
        match = re.search(r'([+-]\d{2}:\d{2})', current_timezone)
        self.timezone.default = match.group(1) if match else "+00:00"
        self.callback = None
    
    async def on_submit(self, interaction: discord.Interaction):
        timezone_str = self.timezone.value.strip()
        
        minutes_offset = parse_timezone(timezone_str)
        if minutes_offset is None:
            await interaction.response.send_message(
                "<:No:825734196256440340> Formato de zona horaria inválido. Usa el formato +HH:MM o -HH:MM.",
                ephemeral=True
            )
            return
        
        formatted_timezone = f"UTC{timezone_str}"
        
        if self.callback:
            await self.callback(interaction, formatted_timezone)
        else:
            await interaction.response.send_message(
                f"Zona horaria configurada: {formatted_timezone}",
                ephemeral=True
            )

class ConfirmDeleteView(ui.View):
    def __init__(self, db, user_id, guild_id):
        super().__init__(timeout=60)
        self.db = db
        self.user_id = user_id
        self.guild_id = guild_id
    
    @ui.button(label="Confirmar", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: ui.Button):
        result = await self.db.delete_birthday(self.user_id, self.guild_id)
        
        if result:
            await interaction.response.edit_message(
                content="<:Si:825734135116070962> Tu cumpleaños ha sido eliminado de este servidor.",
                view=None
            )
        else:
            await interaction.response.edit_message(
                content="<:No:825734196256440340> Error al eliminar tu cumpleaños.",
                view=None
            )
    
    @ui.button(label="Cancelar", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.edit_message(
            content="<:No:825734196256440340> Operación cancelada.",
            view=None
        )

class ConfirmDeleteConfigView(ui.View):
    def __init__(self, bot, db, guild_id):
        super().__init__(timeout=60)
        self.bot = bot
        self.db = db
        self.guild_id = guild_id
    
    @ui.button(label="Confirmar", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: ui.Button):
        result = await self.db.delete_config(self.guild_id)
        
        if result:
            await interaction.response.edit_message(
                content="<:Si:825734135116070962> La configuración de cumpleaños ha sido eliminada.",
                embed=None,
                view=None
            )
        else:
            await interaction.response.edit_message(
                content="<:No:825734196256440340> Error al eliminar la configuración.",
                embed=None,
                view=None
            )
    
    @ui.button(label="Cancelar", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: ui.Button):
        config = await self.db.get_config(self.guild_id)
        view = ConfigView(self.bot, self.db, config)
        
        embed = discord.Embed(
            title="Configuración de Cumpleaños",
            description="Configura cómo se manejarán los mensajes de cumpleaños en el servidor.",
            color=discord.Color.blue()
        )
        
        if config:
            channel = interaction.guild.get_channel(config.get("channel_id"))
            channel_text = f"{channel.mention}" if channel else "No configurado"
            
            embed.add_field(
                name="Canal de felicitaciones",
                value=channel_text,
                inline=False
            )
            
            embed.add_field(
                name="Mensaje de felicitación",
                value=config.get("message", "No configurado"),
                inline=False
            )
            
            embed.add_field(
                name="Zona horaria",
                value=config.get("timezone", "UTC+00:00"),
                inline=False
            )
        
        await interaction.response.edit_message(
            content=None,
            embed=embed,
            view=view
        )