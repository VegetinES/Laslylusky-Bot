import discord
from discord import app_commands
from discord.ext import commands
import asyncio

from database.get import get_specific_field

class Connect4Game:
    def __init__(self, player1, player2):
        self.board = [[0 for _ in range(7)] for _ in range(6)]
        self.player1 = player1
        self.player2 = player2
        self.current_player = player1
        self.winner = None
        self.game_over = False
        
    def make_move(self, column):
        if self.game_over:
            return False
            
        if column < 0 or column >= 7:
            return False
            
        for row in range(5, -1, -1):
            if self.board[row][column] == 0:
                self.board[row][column] = 1 if self.current_player == self.player1 else 2
                
                if self.check_winner(row, column):
                    self.winner = self.current_player
                    self.game_over = True
                elif self.is_board_full():
                    self.game_over = True
                else:
                    self.current_player = self.player2 if self.current_player == self.player1 else self.player1
                
                return True
                
        return False
    
    def check_winner(self, row, column):
        player_value = self.board[row][column]
        
        count = 0
        for c in range(7):
            if self.board[row][c] == player_value:
                count += 1
                if count >= 4:
                    return True
            else:
                count = 0
        
        count = 0
        for r in range(6):
            if self.board[r][column] == player_value:
                count += 1
                if count >= 4:
                    return True
            else:
                count = 0
        
        count = 0
        for i in range(-5, 6):
            r = row - i
            c = column + i
            if 0 <= r < 6 and 0 <= c < 7 and self.board[r][c] == player_value:
                count += 1
                if count >= 4:
                    return True
            else:
                count = 0
        
        count = 0
        for i in range(-5, 6):
            r = row + i
            c = column + i
            if 0 <= r < 6 and 0 <= c < 7 and self.board[r][c] == player_value:
                count += 1
                if count >= 4:
                    return True
            else:
                count = 0
                
        return False
    
    def is_board_full(self):
        for row in self.board:
            if 0 in row:
                return False
        return True
    
    def render_board_embed(self):
        columns = "🇦 🇧 🇨 🇩 🇪 🇫 🇬"
        
        board_str = ""
        for row in self.board:
            for cell in row:
                if cell == 0:
                    board_str += "⚪ "
                elif cell == 1:
                    board_str += "🔴 "
                else:
                    board_str += "🟡 "
            board_str += "\n"
        
        embed = discord.Embed(title="Conecta Cuatro", color=discord.Color.blue())
        embed.description = f"{board_str}\n{columns}"
        
        if self.game_over:
            if self.winner:
                embed.add_field(name="Resultado", value=f"¡{self.winner.mention} ha ganado! 🎉")
            else:
                embed.add_field(name="Resultado", value="¡Empate! 🤝")
        else:
            embed.add_field(name="Turno de", value=self.current_player.mention)
            
        embed.add_field(name="Jugadores", value=f"🔴 {self.player1.mention} vs 🟡 {self.player2.mention}", inline=False)
        
        return embed

class Connect4GameView(discord.ui.View):
    def __init__(self, game):
        super().__init__(timeout=600)
        self.game = game
        self.add_column_buttons()
    
    def add_column_buttons(self):
        columns = [("🇦", 0), ("🇧", 1), ("🇨", 2), ("🇩", 3), ("🇪", 4), ("🇫", 5), ("🇬", 6)]
        
        for label, column in columns:
            button = discord.ui.Button(style=discord.ButtonStyle.secondary, label=label, custom_id=f"column_{column}")
            button.callback = self.make_move_callback
            self.add_item(button)
    
    async def make_move_callback(self, interaction):
        if interaction.user != self.game.current_player:
            await interaction.response.send_message("No es tu turno", ephemeral=True)
            return
            
        custom_id = interaction.data['custom_id']
        column = int(custom_id.split("_")[1])
        
        move_successful = self.game.make_move(column)
        
        if not move_successful:
            await interaction.response.send_message("Columna llena, intenta otra", ephemeral=True)
            return
            
        if self.game.game_over:
            for item in self.children:
                item.disabled = True
        
        await interaction.response.edit_message(embed=self.game.render_board_embed(), view=self)

class Connect4View(discord.ui.View):
    def __init__(self, host, cog):
        super().__init__(timeout=60)
        self.host = host
        self.players = [host]
        self.started = False
        self.message = None
        self.cog = cog
    
    async def on_timeout(self):
        if not self.started and self.message:
            if len(self.players) < 2:
                await self.message.edit(
                    content="El tiempo para unirse a la partida ha expirado y no hay suficientes jugadores.",
                    view=None
                )
            else:
                self.started = True
                await self.start_game()
        
        if self.message and self.message.id in self.cog.active_games:
            del self.cog.active_games[self.message.id]
    
    @discord.ui.button(label="Unirse a la partida", style=discord.ButtonStyle.primary)
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in self.players:
            await interaction.response.send_message("Ya estás en la partida.", ephemeral=True)
            return
        
        if len(self.players) >= 2:
            await interaction.response.send_message("La partida ya está llena.", ephemeral=True)
            return
        
        self.players.append(interaction.user)
        
        embed = discord.Embed(
            title="Partida de Conecta Cuatro",
            description=f"**Anfitrión:** {self.host.mention}\n**Jugadores ({len(self.players)}/2):** {', '.join(p.mention for p in self.players)}",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(f"Te has unido a la partida de Conecta Cuatro.", ephemeral=True)
        await self.message.edit(embed=embed, view=self)
    
    @discord.ui.button(label="Salir de la partida", style=discord.ButtonStyle.secondary)
    async def leave_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user not in self.players:
            await interaction.response.send_message("No estás en la partida.", ephemeral=True)
            return
        
        if interaction.user == self.host:
            if len(self.players) > 1:
                self.players.remove(interaction.user)
                self.host = self.players[0]
            else:
                if self.message.id in self.cog.active_games:
                    del self.cog.active_games[self.message.id]
                await interaction.response.edit_message(
                    content="El anfitrión ha salido. Partida cancelada.",
                    view=None
                )
                return
        else:
            self.players.remove(interaction.user)
        
        embed = discord.Embed(
            title="Partida de Conecta Cuatro",
            description=f"**Anfitrión:** {self.host.mention}\n**Jugadores ({len(self.players)}/2):** {', '.join(p.mention for p in self.players)}",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(f"Has salido de la partida.", ephemeral=True)
        await self.message.edit(embed=embed, view=self)
    
    @discord.ui.button(label="Iniciar partida", style=discord.ButtonStyle.success)
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.host:
            await interaction.response.send_message("Solo el anfitrión puede iniciar la partida.", ephemeral=True)
            return
        
        if len(self.players) < 2:
            await interaction.response.send_message("Se necesitan 2 jugadores para iniciar la partida.", ephemeral=True)
            return
        
        self.started = True
        self.stop()
        
        await interaction.response.send_message("Iniciando partida de Conecta Cuatro...", ephemeral=True)
        await self.start_game()
    
    async def start_game(self):
        game = Connect4Game(self.players[0], self.players[1])
        game_view = Connect4GameView(game)
        
        await self.message.edit(
            content=f"¡Partida iniciada! Turno de {self.players[0].mention}",
            embed=game.render_board_embed(),
            view=game_view
        )
        
        if self.message.id in self.cog.active_games:
            del self.cog.active_games[self.message.id]

class Connect4(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}

    @commands.command(name="conecta4")
    async def conecta4_text(self, ctx):
        act_commands = get_specific_field(ctx.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if "conecta4" not in act_commands:
            await ctx.reply("El comando no está activado en este servidor.")
            return
        
        for game_id, game_data in self.active_games.items():
            if len(game_data.players) < 2 and not game_data.started:
                game_data.players.append(ctx.author)
                
                embed = discord.Embed(
                    title="Partida de Conecta Cuatro",
                    description=f"**Anfitrión:** {game_data.host.mention}\n**Jugadores ({len(game_data.players)}/2):** {', '.join(p.mention for p in game_data.players)}",
                    color=discord.Color.green()
                )
                
                await game_data.message.edit(embed=embed, view=game_data)
                await ctx.send(f"{ctx.author.mention} se ha unido a una partida existente de Conecta Cuatro.", delete_after=3)
                return
        
        view = Connect4View(ctx.author, self)
        
        embed = discord.Embed(
            title="Partida de Conecta Cuatro",
            description=f"**Anfitrión:** {ctx.author.mention}\n**Jugadores (1/2):** {ctx.author.mention}",
            color=discord.Color.green()
        )
        
        message = await ctx.send(embed=embed, view=view)
        view.message = message
        self.active_games[message.id] = view

    @app_commands.command(name="conecta4", description="Únete o crea una partida de Conecta Cuatro")
    async def conectacuatro(self, interaction: discord.Interaction):
        act_commands = get_specific_field(interaction.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
            return
        
        if "conecta4" not in act_commands:
            await interaction.response.send_message("El comando no está activado en este servidor.")
            return

        for game_id, game_data in self.active_games.items():
            if len(game_data.players) < 2 and not game_data.started:
                game_data.players.append(interaction.user)
                
                embed = discord.Embed(
                    title="Partida de Conecta Cuatro",
                    description=f"**Anfitrión:** {game_data.host.mention}\n**Jugadores ({len(game_data.players)}/2):** {', '.join(p.mention for p in game_data.players)}",
                    color=discord.Color.green()
                )
                
                await game_data.message.edit(embed=embed, view=game_data)
                await interaction.response.send_message(f"Te has unido a una partida existente de Conecta Cuatro.", ephemeral=True)
                return

        view = Connect4View(interaction.user, self)
        
        embed = discord.Embed(
            title="Partida de Conecta Cuatro",
            description=f"**Anfitrión:** {interaction.user.mention}\n**Jugadores (1/2):** {interaction.user.mention}",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed, view=view)
        
        message = await interaction.original_response()
        view.message = message
        self.active_games[message.id] = view

async def setup(bot):
    await bot.add_cog(Connect4(bot))