import discord
from discord import ui

class ChannelSelectorView(ui.View):
    def __init__(self, bot, config):
        super().__init__(timeout=300)
        self.bot = bot
        self.config = config
        self.current_page = 0
        
        self.update_selector()
    
    def update_selector(self):
        for item in self.children[:]:
            if isinstance(item, ui.Select):
                self.remove_item(item)
        
        guild = self.bot.get_guild(self.config.get("guild_id"))
        if not guild:
            return
            
        voice_channels = guild.voice_channels
        
        start_idx = self.current_page * 25
        end_idx = min(start_idx + 25, len(voice_channels))
        
        options = []
        for channel in voice_channels[start_idx:end_idx]:
            options.append(
                discord.SelectOption(
                    label=channel.name[:25],
                    description=f"ID: {channel.id}",
                    value=str(channel.id)
                )
            )
        
        if options:
            channel_select = ui.Select(
                placeholder=f"Selecciona un canal (Página {self.current_page+1}/{max(1, (len(voice_channels)-1)//25+1)})",
                options=options,
                custom_id="channel_select"
            )
            channel_select.callback = self.channel_select_callback
            self.add_item(channel_select)
            
            if len(voice_channels) > 25:
                for item in self.children[:]:
                    if isinstance(item, ui.Button) and item.custom_id in ["prev_page", "next_page"]:
                        self.remove_item(item)
                
                prev_btn = ui.Button(
                    label="◀️ Anterior", 
                    style=discord.ButtonStyle.secondary,
                    custom_id="prev_page",
                    disabled=(self.current_page == 0),
                    row=1
                )
                prev_btn.callback = self.prev_page
                self.add_item(prev_btn)
                
                max_pages = (len(voice_channels) - 1) // 25
                next_btn = ui.Button(
                    label="Siguiente ▶️", 
                    style=discord.ButtonStyle.secondary,
                    custom_id="next_page",
                    disabled=(self.current_page >= max_pages),
                    row=1
                )
                next_btn.callback = self.next_page
                self.add_item(next_btn)
    
    async def prev_page(self, interaction: discord.Interaction):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_selector()
            await interaction.response.edit_message(view=self)
    
    async def next_page(self, interaction: discord.Interaction):
        guild = self.bot.get_guild(self.config.get("guild_id"))
        if not guild:
            return
        
        voice_channels = guild.voice_channels
        max_pages = (len(voice_channels) - 1) // 25
        
        if self.current_page < max_pages:
            self.current_page += 1
            self.update_selector()
            await interaction.response.edit_message(view=self)
            
    async def channel_select_callback(self, interaction: discord.Interaction):
        channel_id = int(interaction.data["values"][0])
        channel = interaction.guild.get_channel(channel_id)
        
        if not channel:
            await interaction.response.send_message(
                "❌ No se encontró el canal seleccionado.",
                ephemeral=True
            )
            return
        
        self.config["generator_channel"] = channel_id
        
        from .setup_view import VoiceSetupView
        view = VoiceSetupView(self.bot, self.config)
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="Canal generador configurado",
                description=f"Has seleccionado {channel.mention} como canal generador.",
                color=discord.Color.green()
            ),
            view=view
        )

class CategorySelectorView(ui.View):
    def __init__(self, bot, config):
        super().__init__(timeout=300)
        self.bot = bot
        self.config = config
        
        options = []
        for category in self.bot.get_guild(self.config.get("guild_id")).categories:
            options.append(
                discord.SelectOption(
                    label=category.name,
                    description=f"ID: {category.id}",
                    value=str(category.id)
                )
            )
        
        if options:
            category_select = ui.Select(
                placeholder="Selecciona una categoría",
                options=options[:25],
                custom_id="category_select"
            )
            category_select.callback = self.category_select_callback
            self.add_item(category_select)
    
    async def category_select_callback(self, interaction: discord.Interaction):
        category_id = int(interaction.data["values"][0])
        category = interaction.guild.get_channel(category_id)
        
        if not category:
            await interaction.response.send_message(
                "❌ No se encontró la categoría seleccionada.",
                ephemeral=True
            )
            return
        
        self.config["category_id"] = category_id
        
        from .setup_view import VoiceSetupView
        view = VoiceSetupView(self.bot, self.config)
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="Categoría configurada",
                description=f"Has seleccionado la categoría **{category.name}** para los canales personalizados.",
                color=discord.Color.green()
            ),
            view=view
        )
    
    @ui.button(label="Volver", style=discord.ButtonStyle.secondary)
    async def back_button(self, interaction: discord.Interaction, button: ui.Button):
        from .setup_view import VoiceSetupView
        view = VoiceSetupView(self.bot, self.config)
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="Configuración de Canales de Voz Dinámicos",
                description="Configura el sistema de canales de voz dinámicos.",
                color=discord.Color.blue()
            ),
            view=view
        )