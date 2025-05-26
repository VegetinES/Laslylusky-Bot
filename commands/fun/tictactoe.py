import discord
from discord.ext import commands
from discord import app_commands
import asyncio

from database.get import get_specific_field

class TicTacToeButton(discord.ui.Button):
    def __init__(self, x, y):
        super().__init__(style=discord.ButtonStyle.secondary, label="\u200b", row=y)
        self.x = x
        self.y = y

    async def callback(self, interaction: discord.Interaction):
        view: TicTacToeGameView = self.view
        
        if interaction.user != view.current_player:
            return await interaction.response.send_message("No es tu turno.", ephemeral=True)
        
        if self.label not in ["\u200b", " "]:
            return await interaction.response.send_message("Esta casilla ya está ocupada.", ephemeral=True)
            
        self.label = view.current_symbol
        self.style = discord.ButtonStyle.danger if view.current_symbol == "X" else discord.ButtonStyle.success
        self.disabled = False

        view.board[self.y][self.x] = view.current_symbol
        
        winner = view.check_winner()
        if winner:
            view.end_game(winner)
            await interaction.response.edit_message(content=f"¡**{view.current_player.display_name}** ha ganado!", view=view)
            return
        
        if view.is_board_full():
            view.end_game(None)
            await interaction.response.edit_message(content="¡Empate! No hay ganador.", view=view)
            return
        
        view.current_player = view.player2 if view.current_player == view.player1 else view.player1
        view.current_symbol = "O" if view.current_symbol == "X" else "X"
        
        await interaction.response.edit_message(content=f"Turno de **{view.current_player.display_name}** ({view.current_symbol})", view=view)

class TicTacToeGameView(discord.ui.View):
    def __init__(self, player1, player2):
        super().__init__(timeout=300)
        self.player1 = player1
        self.player2 = player2
        self.current_player = player1
        self.current_symbol = "X"
        self.board = [[" " for _ in range(3)] for _ in range(3)]
        
        for y in range(3):
            for x in range(3):
                self.add_item(TicTacToeButton(x, y))
    
    def check_winner(self):
        for row in self.board:
            if row[0] == row[1] == row[2] != " ":
                return row[0]
        
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] != " ":
                return self.board[0][col]
        
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != " ":
            return self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != " ":
            return self.board[0][2]
        
        return None
    
    def is_board_full(self):
        for row in self.board:
            if " " in row:
                return False
        return True
    
    def end_game(self, winner):
        for child in self.children:
            child.disabled = True

class TicTacToeView(discord.ui.View):
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
            title="Partida de Tres en Raya",
            description=f"**Anfitrión:** {self.host.mention}\n**Jugadores ({len(self.players)}/2):** {', '.join(p.mention for p in self.players)}",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(f"Te has unido a la partida de Tres en Raya.", ephemeral=True)
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
            title="Partida de Tres en Raya",
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
        
        await interaction.response.send_message("Iniciando partida de Tres en Raya...", ephemeral=True)
        await self.start_game()
    
    async def start_game(self):
        game_view = TicTacToeGameView(self.players[0], self.players[1])
        
        await self.message.edit(
            content=f"¡Partida iniciada! Turno de **{self.players[0].display_name}** (X)",
            embed=None,
            view=game_view
        )
        
        if self.message.id in self.cog.active_games:
            del self.cog.active_games[self.message.id]

class TicTacToeCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}

    @commands.command(name="tictactoe")
    async def tictactoe_command(self, ctx):
        act_commands = get_specific_field(ctx.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if "tictactoe" not in act_commands:
            await ctx.reply("El comando no está activado en este servidor.")
            return
        
        for game_id, game_data in self.active_games.items():
            if len(game_data.players) < 2 and not game_data.started:
                game_data.players.append(ctx.author)
                
                embed = discord.Embed(
                    title="Partida de Tres en Raya",
                    description=f"**Anfitrión:** {game_data.host.mention}\n**Jugadores ({len(game_data.players)}/2):** {', '.join(p.mention for p in game_data.players)}",
                    color=discord.Color.green()
                )
                
                await game_data.message.edit(embed=embed, view=game_data)
                await ctx.send(f"{ctx.author.mention} se ha unido a una partida existente de Tres en Raya.", delete_after=3)
                return
        
        view = TicTacToeView(ctx.author, self)
        
        embed = discord.Embed(
            title="Partida de Tres en Raya",
            description=f"**Anfitrión:** {ctx.author.mention}\n**Jugadores (1/2):** {ctx.author.mention}",
            color=discord.Color.green()
        )
        
        message = await ctx.send(embed=embed, view=view)
        view.message = message
        self.active_games[message.id] = view

    @app_commands.command(name="tictactoe", description="Únete o crea una partida de tres en raya")
    async def tictactoe_slash(self, interaction: discord.Interaction):
        act_commands = get_specific_field(interaction.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
            return
        
        if "tictactoe" not in act_commands:
            await interaction.response.send_message("El comando no está activado en este servidor.")
            return
        
        for game_id, game_data in self.active_games.items():
            if len(game_data.players) < 2 and not game_data.started:
                game_data.players.append(interaction.user)
                
                embed = discord.Embed(
                    title="Partida de Tres en Raya",
                    description=f"**Anfitrión:** {game_data.host.mention}\n**Jugadores ({len(game_data.players)}/2):** {', '.join(p.mention for p in game_data.players)}",
                    color=discord.Color.green()
                )
                
                await game_data.message.edit(embed=embed, view=game_data)
                await interaction.response.send_message(f"Te has unido a una partida existente de Tres en Raya.", ephemeral=True)
                return
        
        view = TicTacToeView(interaction.user, self)
        
        embed = discord.Embed(
            title="Partida de Tres en Raya",
            description=f"**Anfitrión:** {interaction.user.mention}\n**Jugadores (1/2):** {interaction.user.mention}",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed, view=view)
        
        message = await interaction.original_response()
        view.message = message
        self.active_games[message.id] = view

async def setup(bot):
    await bot.add_cog(TicTacToeCommand(bot))