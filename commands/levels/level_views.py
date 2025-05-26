import discord
from .level_manager import LevelManager
from .helpers import create_leaderboard_embed

class LeaderboardView(discord.ui.View):
    def __init__(self, bot, guild_id):
        super().__init__(timeout=300)
        self.bot = bot
        self.level_manager = LevelManager(bot)
        self.guild_id = guild_id
        self.current_page = 0
        self.users_per_page = 10
    
    async def update_message(self, interaction):
        page = self.current_page
        users_data = self.level_manager.get_top_users(self.guild_id, page, self.users_per_page)
        total_users = self.level_manager.count_ranked_users(self.guild_id)
        total_pages = max(1, (total_users + self.users_per_page - 1) // self.users_per_page)
        
        if self.current_page >= total_pages:
            self.current_page = total_pages - 1
            page = self.current_page
            users_data = self.level_manager.get_top_users(self.guild_id, page, self.users_per_page)
        
        guild = self.bot.get_guild(self.guild_id)
        embed = create_leaderboard_embed(guild, users_data, page, total_pages)
        
        for i, button in enumerate(self.children):
            if i == 0:
                button.disabled = (page == 0)
            elif i == 1:
                button.disabled = (page == 0)
            elif i == 2:
                button.disabled = (page >= total_pages - 1)
            elif i == 3:
                button.disabled = (page >= total_pages - 1)
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="Primera", style=discord.ButtonStyle.secondary)
    async def first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = 0
        await self.update_message(interaction)
    
    @discord.ui.button(label="Anterior", style=discord.ButtonStyle.primary)
    async def prev_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
        await self.update_message(interaction)
    
    @discord.ui.button(label="Siguiente", style=discord.ButtonStyle.primary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page += 1
        await self.update_message(interaction)
    
    @discord.ui.button(label="Última", style=discord.ButtonStyle.secondary)
    async def last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        total_users = self.level_manager.count_ranked_users(self.guild_id)
        self.current_page = (total_users - 1) // self.users_per_page
        await self.update_message(interaction)