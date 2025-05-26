import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from commands.fun.gamesstatistics.hangman_stats import get_hangman_stats_embed
from commands.fun.gamesstatistics.minesweeper_stats import get_minesweeper_stats_embed
from commands.fun.gamesstatistics.blackjack_stats import get_blackjack_stats_embed
from database.minigames import get_user_stats, get_top_players, get_game_stats

class GameStatistics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="estadisticas-juegos")
    async def game_stats_cmd(self, ctx):
        view = GameStatsMainView(self.bot, ctx.author)
        embed = await self.create_main_embed(ctx.author)
        
        await ctx.send(embed=embed, view=view)
    
    @app_commands.command(name="estadisticas-juegos", description="Muestra tus estadísticas de juegos")
    async def game_stats_slash(self, interaction: discord.Interaction):
        view = GameStatsMainView(self.bot, interaction.user)
        embed = await self.create_main_embed(interaction.user)
        
        await interaction.response.send_message(embed=embed, view=view)
    
    async def create_main_embed(self, user):
        embed = discord.Embed(
            title="Estadísticas de Juegos",
            description=f"Selecciona un juego para ver tus estadísticas, {user.display_name}",
            color=0x00BFFF
        )
        
        hangman_stats = get_user_stats(user.id, 'hangman')
        minesweeper_stats = get_user_stats(user.id, 'minesweeper')
        blackjack_stats = get_user_stats(user.id, 'blackjack')
        
        embed.add_field(
            name="🎮 Juegos Disponibles",
            value="• 🎯 Ahorcado\n• 💣 Buscaminas\n• 🃏 Blackjack",
            inline=False
        )
        
        embed.add_field(
            name="🎯 Ahorcado",
            value=(
                f"Partidas: {hangman_stats.get('total_games', 0)}\n"
                f"Victorias: {hangman_stats.get('wins', 0)}\n"
                f"Puntos: {hangman_stats.get('points', 0)}"
            ),
            inline=True
        )
        
        embed.add_field(
            name="💣 Buscaminas",
            value=(
                f"Partidas: {minesweeper_stats.get('total_games', 0)}\n"
                f"Victorias: {minesweeper_stats.get('wins', 0)}\n"
                f"Puntos: {minesweeper_stats.get('points', 0)}"
            ),
            inline=True
        )
        
        embed.add_field(
            name="🃏 Blackjack",
            value=(
                f"Partidas: {blackjack_stats.get('total_games', 0)}\n"
                f"Victorias: {blackjack_stats.get('wins', 0)}\n"
                f"Puntos: {blackjack_stats.get('points', 0)}"
            ),
            inline=True
        )
        
        embed.set_footer(text="Usa el menú desplegable para ver estadísticas detalladas")
        return embed

class GameStatsMainView(discord.ui.View):
    def __init__(self, bot, user):
        super().__init__(timeout=300)
        self.bot = bot
        self.user = user
        self.add_item(GameSelectDropdown(bot, user))

class GameSelectDropdown(discord.ui.Select):
    def __init__(self, bot, user):
        self.bot = bot
        self.user = user
        
        options = [
            discord.SelectOption(
                label="Ahorcado",
                description="Ver estadísticas del juego del ahorcado",
                value="hangman",
                emoji="🎯"
            ),
            discord.SelectOption(
                label="Buscaminas",
                description="Ver estadísticas del juego del buscaminas",
                value="minesweeper",
                emoji="💣"
            ),
            discord.SelectOption(
                label="Blackjack",
                description="Ver estadísticas del juego del blackjack",
                value="blackjack",
                emoji="🃏"
            )
        ]
        
        super().__init__(
            placeholder="Selecciona un juego",
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("Esta no es tu estadística.", ephemeral=True)
            return
        
        game_type = self.values[0]
        
        if game_type == "hangman":
            user_stats = get_user_stats(self.user.id, 'hangman')
            
            class HangmanStatsMainView(discord.ui.View):
                def __init__(self, original_user):
                    super().__init__(timeout=300)
                    self.user = original_user
                    self.current_page = 0
                    
                    prev_button = discord.ui.Button(
                        style=discord.ButtonStyle.secondary,
                        label="◀️ Anterior",
                        custom_id="prev_page",
                        disabled=True
                    )
                    prev_button.callback = self.prev_page_callback
                    self.add_item(prev_button)
                    
                    next_button = discord.ui.Button(
                        style=discord.ButtonStyle.secondary,
                        label="Siguiente ▶️",
                        custom_id="next_page",
                        disabled=False
                    )
                    next_button.callback = self.next_page_callback
                    self.add_item(next_button)
                    
                    back_button = discord.ui.Button(
                        style=discord.ButtonStyle.primary,
                        label="Volver al menú principal",
                        custom_id="back_main"
                    )
                    back_button.callback = self.back_to_main
                    self.add_item(back_button)
                
                async def prev_page_callback(self, button_interaction: discord.Interaction):
                    if button_interaction.user.id != self.user.id:
                        await button_interaction.response.send_message("Esta no es tu estadística.", ephemeral=True)
                        return
                    
                    self.current_page = max(0, self.current_page - 1)
                    stats = get_user_stats(self.user.id, 'hangman')
                    embed = get_hangman_stats_embed(self.user, stats, self.current_page)
                    
                    for item in self.children:
                        if item.custom_id == "prev_page":
                            item.disabled = self.current_page == 0
                        elif item.custom_id == "next_page":
                            item.disabled = self.current_page == 2
                    
                    await button_interaction.response.edit_message(embed=embed, view=self)
                
                async def next_page_callback(self, button_interaction: discord.Interaction):
                    if button_interaction.user.id != self.user.id:
                        await button_interaction.response.send_message("Esta no es tu estadística.", ephemeral=True)
                        return
                    
                    self.current_page = min(2, self.current_page + 1)
                    stats = get_user_stats(self.user.id, 'hangman')
                    embed = get_hangman_stats_embed(self.user, stats, self.current_page)
                    
                    for item in self.children:
                        if item.custom_id == "prev_page":
                            item.disabled = self.current_page == 0
                        elif item.custom_id == "next_page":
                            item.disabled = self.current_page == 2
                    
                    await button_interaction.response.edit_message(embed=embed, view=self)
                
                async def back_to_main(self, button_interaction: discord.Interaction):
                    if button_interaction.user.id != self.user.id:
                        await button_interaction.response.send_message("Esta no es tu estadística.", ephemeral=True)
                        return
                    
                    view = GameStatsMainView(self.bot, self.user)
                    
                    embed = discord.Embed(
                        title="Estadísticas de Juegos",
                        description=f"Selecciona un juego para ver tus estadísticas, {self.user.display_name}",
                        color=0x00BFFF
                    )
                    
                    hangman_stats = get_user_stats(self.user.id, 'hangman')
                    minesweeper_stats = get_user_stats(self.user.id, 'minesweeper')
                    blackjack_stats = get_user_stats(self.user.id, 'blackjack')
                    
                    embed.add_field(
                        name="🎮 Juegos Disponibles",
                        value="• 🎯 Ahorcado\n• 💣 Buscaminas\n• 🃏 Blackjack",
                        inline=False
                    )
                    
                    embed.add_field(
                        name="🎯 Ahorcado",
                        value=(
                            f"Partidas: {hangman_stats.get('total_games', 0)}\n"
                            f"Victorias: {hangman_stats.get('wins', 0)}\n"
                            f"Puntos: {hangman_stats.get('points', 0)}"
                        ),
                        inline=True
                    )
                    
                    embed.add_field(
                        name="💣 Buscaminas",
                        value=(
                            f"Partidas: {minesweeper_stats.get('total_games', 0)}\n"
                            f"Victorias: {minesweeper_stats.get('wins', 0)}\n"
                            f"Puntos: {minesweeper_stats.get('points', 0)}"
                        ),
                        inline=True
                    )
                    
                    embed.add_field(
                        name="🃏 Blackjack",
                        value=(
                            f"Partidas: {blackjack_stats.get('total_games', 0)}\n"
                            f"Victorias: {blackjack_stats.get('wins', 0)}\n"
                            f"Puntos: {blackjack_stats.get('points', 0)}"
                        ),
                        inline=True
                    )
                    
                    embed.set_footer(text="Usa el menú desplegable para ver estadísticas detalladas")
                    
                    await button_interaction.response.edit_message(embed=embed, view=view)
            
            hangman_view = HangmanStatsMainView(self.user)
            hangman_view.bot = self.bot
            
            embed = get_hangman_stats_embed(self.user, user_stats, 0)
            
            await interaction.response.edit_message(embed=embed, view=hangman_view)
            
        elif game_type == "minesweeper":
            user_stats = get_user_stats(self.user.id, 'minesweeper')
            
            class MinesweeperStatsMainView(discord.ui.View):
                def __init__(self, original_user):
                    super().__init__(timeout=300)
                    self.user = original_user
                    self.current_page = 0
                    
                    prev_button = discord.ui.Button(
                        style=discord.ButtonStyle.secondary,
                        label="◀️ Anterior",
                        custom_id="prev_page",
                        disabled=True
                    )
                    prev_button.callback = self.prev_page_callback
                    self.add_item(prev_button)
                    
                    next_button = discord.ui.Button(
                        style=discord.ButtonStyle.secondary,
                        label="Siguiente ▶️",
                        custom_id="next_page",
                        disabled=False
                    )
                    next_button.callback = self.next_page_callback
                    self.add_item(next_button)
                    
                    back_button = discord.ui.Button(
                        style=discord.ButtonStyle.primary,
                        label="Volver al menú principal",
                        custom_id="back_main"
                    )
                    back_button.callback = self.back_to_main
                    self.add_item(back_button)
                
                async def prev_page_callback(self, button_interaction: discord.Interaction):
                    if button_interaction.user.id != self.user.id:
                        await button_interaction.response.send_message("Esta no es tu estadística.", ephemeral=True)
                        return
                    
                    self.current_page = max(0, self.current_page - 1)
                    stats = get_user_stats(self.user.id, 'minesweeper')
                    embed = get_minesweeper_stats_embed(self.user, stats, self.current_page)
                    
                    for item in self.children:
                        if item.custom_id == "prev_page":
                            item.disabled = self.current_page == 0
                        elif item.custom_id == "next_page":
                            item.disabled = self.current_page == 2
                    
                    await button_interaction.response.edit_message(embed=embed, view=self)
                
                async def next_page_callback(self, button_interaction: discord.Interaction):
                    if button_interaction.user.id != self.user.id:
                        await button_interaction.response.send_message("Esta no es tu estadística.", ephemeral=True)
                        return
                    
                    self.current_page = min(2, self.current_page + 1)
                    stats = get_user_stats(self.user.id, 'minesweeper')
                    embed = get_minesweeper_stats_embed(self.user, stats, self.current_page)
                    
                    for item in self.children:
                        if item.custom_id == "prev_page":
                            item.disabled = self.current_page == 0
                        elif item.custom_id == "next_page":
                            item.disabled = self.current_page == 2
                    
                    await button_interaction.response.edit_message(embed=embed, view=self)
                
                async def back_to_main(self, button_interaction: discord.Interaction):
                    if button_interaction.user.id != self.user.id:
                        await button_interaction.response.send_message("Esta no es tu estadística.", ephemeral=True)
                        return
                    
                    view = GameStatsMainView(self.bot, self.user)
                    
                    embed = discord.Embed(
                        title="Estadísticas de Juegos",
                        description=f"Selecciona un juego para ver tus estadísticas, {self.user.display_name}",
                        color=0x00BFFF
                    )
                    
                    hangman_stats = get_user_stats(self.user.id, 'hangman')
                    minesweeper_stats = get_user_stats(self.user.id, 'minesweeper')
                    blackjack_stats = get_user_stats(self.user.id, 'blackjack')
                    
                    embed.add_field(
                        name="🎮 Juegos Disponibles",
                        value="• 🎯 Ahorcado\n• 💣 Buscaminas\n• 🃏 Blackjack",
                        inline=False
                    )
                    
                    embed.add_field(
                        name="🎯 Ahorcado",
                        value=(
                            f"Partidas: {hangman_stats.get('total_games', 0)}\n"
                            f"Victorias: {hangman_stats.get('wins', 0)}\n"
                            f"Puntos: {hangman_stats.get('points', 0)}"
                        ),
                        inline=True
                    )
                    
                    embed.add_field(
                        name="💣 Buscaminas",
                        value=(
                            f"Partidas: {minesweeper_stats.get('total_games', 0)}\n"
                            f"Victorias: {minesweeper_stats.get('wins', 0)}\n"
                            f"Puntos: {minesweeper_stats.get('points', 0)}"
                        ),
                        inline=True
                    )
                    
                    embed.add_field(
                        name="🃏 Blackjack",
                        value=(
                            f"Partidas: {blackjack_stats.get('total_games', 0)}\n"
                            f"Victorias: {blackjack_stats.get('wins', 0)}\n"
                            f"Puntos: {blackjack_stats.get('points', 0)}"
                        ),
                        inline=True
                    )
                    
                    embed.set_footer(text="Usa el menú desplegable para ver estadísticas detalladas")
                    
                    await button_interaction.response.edit_message(embed=embed, view=view)
            
            minesweeper_view = MinesweeperStatsMainView(self.user)
            minesweeper_view.bot = self.bot
            
            embed = get_minesweeper_stats_embed(self.user, user_stats, 0)
            
            await interaction.response.edit_message(embed=embed, view=minesweeper_view)
            
        elif game_type == "blackjack":
            user_stats = get_user_stats(self.user.id, 'blackjack')
            
            class BlackjackStatsMainView(discord.ui.View):
                def __init__(self, original_user):
                    super().__init__(timeout=300)
                    self.user = original_user
                    self.current_page = 0
                    
                    prev_button = discord.ui.Button(
                        style=discord.ButtonStyle.secondary,
                        label="◀️ Anterior",
                        custom_id="prev_page",
                        disabled=True
                    )
                    prev_button.callback = self.prev_page_callback
                    self.add_item(prev_button)
                    
                    next_button = discord.ui.Button(
                        style=discord.ButtonStyle.secondary,
                        label="Siguiente ▶️",
                        custom_id="next_page",
                        disabled=False
                    )
                    next_button.callback = self.next_page_callback
                    self.add_item(next_button)
                    
                    back_button = discord.ui.Button(
                        style=discord.ButtonStyle.primary,
                        label="Volver al menú principal",
                        custom_id="back_main"
                    )
                    back_button.callback = self.back_to_main
                    self.add_item(back_button)
                
                async def prev_page_callback(self, button_interaction: discord.Interaction):
                    if button_interaction.user.id != self.user.id:
                        await button_interaction.response.send_message("Esta no es tu estadística.", ephemeral=True)
                        return
                    
                    self.current_page = max(0, self.current_page - 1)
                    stats = get_user_stats(self.user.id, 'blackjack')
                    embed = get_blackjack_stats_embed(self.user, stats, self.current_page)
                    
                    for item in self.children:
                        if item.custom_id == "prev_page":
                            item.disabled = self.current_page == 0
                        elif item.custom_id == "next_page":
                            item.disabled = self.current_page == 2
                    
                    await button_interaction.response.edit_message(embed=embed, view=self)
                
                async def next_page_callback(self, button_interaction: discord.Interaction):
                    if button_interaction.user.id != self.user.id:
                        await button_interaction.response.send_message("Esta no es tu estadística.", ephemeral=True)
                        return
                    
                    self.current_page = min(2, self.current_page + 1)
                    stats = get_user_stats(self.user.id, 'blackjack')
                    embed = get_blackjack_stats_embed(self.user, stats, self.current_page)
                    
                    for item in self.children:
                        if item.custom_id == "prev_page":
                            item.disabled = self.current_page == 0
                        elif item.custom_id == "next_page":
                            item.disabled = self.current_page == 2
                    
                    await button_interaction.response.edit_message(embed=embed, view=self)
                
                async def back_to_main(self, button_interaction: discord.Interaction):
                    if button_interaction.user.id != self.user.id:
                        await button_interaction.response.send_message("Esta no es tu estadística.", ephemeral=True)
                        return
                    
                    view = GameStatsMainView(self.bot, self.user)
                    
                    embed = discord.Embed(
                        title="Estadísticas de Juegos",
                        description=f"Selecciona un juego para ver tus estadísticas, {self.user.display_name}",
                        color=0x00BFFF
                    )
                    
                    hangman_stats = get_user_stats(self.user.id, 'hangman')
                    minesweeper_stats = get_user_stats(self.user.id, 'minesweeper')
                    blackjack_stats = get_user_stats(self.user.id, 'blackjack')
                    
                    embed.add_field(
                        name="🎮 Juegos Disponibles",
                        value="• 🎯 Ahorcado\n• 💣 Buscaminas\n• 🃏 Blackjack",
                        inline=False
                    )
                    
                    embed.add_field(
                        name="🎯 Ahorcado",
                        value=(
                            f"Partidas: {hangman_stats.get('total_games', 0)}\n"
                            f"Victorias: {hangman_stats.get('wins', 0)}\n"
                            f"Puntos: {hangman_stats.get('points', 0)}"
                        ),
                        inline=True
                    )
                    
                    embed.add_field(
                        name="💣 Buscaminas",
                        value=(
                            f"Partidas: {minesweeper_stats.get('total_games', 0)}\n"
                            f"Victorias: {minesweeper_stats.get('wins', 0)}\n"
                            f"Puntos: {minesweeper_stats.get('points', 0)}"
                        ),
                        inline=True
                    )
                    
                    embed.add_field(
                        name="🃏 Blackjack",
                        value=(
                            f"Partidas: {blackjack_stats.get('total_games', 0)}\n"
                            f"Victorias: {blackjack_stats.get('wins', 0)}\n"
                            f"Puntos: {blackjack_stats.get('points', 0)}"
                        ),
                        inline=True
                    )
                    
                    embed.set_footer(text="Usa el menú desplegable para ver estadísticas detalladas")
                    
                    await button_interaction.response.edit_message(embed=embed, view=view)
            
            blackjack_view = BlackjackStatsMainView(self.user)
            blackjack_view.bot = self.bot
            
            embed = get_blackjack_stats_embed(self.user, user_stats, 0)
            
            await interaction.response.edit_message(embed=embed, view=blackjack_view)

async def setup(bot):
    await bot.add_cog(GameStatistics(bot))