import discord
from discord import app_commands
from discord.ext import commands
import random
import asyncio

from database.get import get_specific_field

class RPSGameView(discord.ui.View):
    def __init__(self, player1, player2):
        super().__init__(timeout=30)
        self.player1 = player1
        self.player2 = player2
        self.player1_choice = None
        self.player2_choice = None
        self.message = None
        
    async def on_timeout(self):
        if not self.player1_choice and not self.player2_choice:
            await self.message.edit(content=f"El juego ha terminado. Nadie ha elegido una opción.", view=None)
        elif not self.player1_choice:
            await self.message.edit(content=f"El juego ha terminado. {self.player1.mention} no eligió a tiempo.", view=None)
        elif not self.player2_choice:
            await self.message.edit(content=f"El juego ha terminado. {self.player2.mention} no eligió a tiempo.", view=None)
    
    @discord.ui.button(label="Piedra", style=discord.ButtonStyle.primary, emoji="🪨")
    async def rock(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_choice(interaction, "piedra")
    
    @discord.ui.button(label="Papel", style=discord.ButtonStyle.success, emoji="📄")
    async def paper(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_choice(interaction, "papel")
    
    @discord.ui.button(label="Tijera", style=discord.ButtonStyle.danger, emoji="✂️")
    async def scissors(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_choice(interaction, "tijera")
    
    async def process_choice(self, interaction: discord.Interaction, choice):
        if interaction.user.id != self.player1.id and interaction.user.id != self.player2.id:
            await interaction.response.send_message("No eres parte de este juego.", ephemeral=True)
            return
        
        if (interaction.user.id == self.player1.id and self.player1_choice) or \
           (interaction.user.id == self.player2.id and self.player2_choice):
            await interaction.response.send_message("Ya has hecho tu elección.", ephemeral=True)
            return
        
        if interaction.user.id == self.player1.id:
            self.player1_choice = choice
            await interaction.response.send_message(f"Has elegido {choice}.", ephemeral=True)
        else:
            self.player2_choice = choice
            await interaction.response.send_message(f"Has elegido {choice}.", ephemeral=True)
        
        if self.player1_choice and self.player2_choice:
            self.stop()
            
            result = self.determine_winner()
            
            await self.message.edit(
                content=f"**¡El juego ha terminado!**\n\n"
                      f"{self.player1.mention} eligió: {self.player1_choice}\n"
                      f"{self.player2.mention} eligió: {self.player2_choice}\n\n"
                      f"{result}",
                view=None
            )
    
    def determine_winner(self):
        if self.player1_choice == self.player2_choice:
            return "¡Empate!"
        
        if (self.player1_choice == "piedra" and self.player2_choice == "tijera") or \
           (self.player1_choice == "papel" and self.player2_choice == "piedra") or \
           (self.player1_choice == "tijera" and self.player2_choice == "papel"):
            return f"**{self.player1.display_name} gana!** 🏆"
        else:
            return f"**{self.player2.display_name} gana!** 🏆"

class RPSView(discord.ui.View):
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
            title="Partida de Piedra, Papel o Tijera",
            description=f"**Anfitrión:** {self.host.mention}\n**Jugadores ({len(self.players)}/2):** {', '.join(p.mention for p in self.players)}",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(f"Te has unido a la partida de Piedra, Papel o Tijera.", ephemeral=True)
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
            title="Partida de Piedra, Papel o Tijera",
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
        
        await interaction.response.send_message("Iniciando partida de Piedra, Papel o Tijera...", ephemeral=True)
        await self.start_game()
    
    async def start_game(self):
        game_view = RPSGameView(self.players[0], self.players[1])
        game_view.message = self.message
        
        await self.message.edit(
            content=f"**Piedra, Papel o Tijera**\n\n"
                   f"{self.players[0].mention} vs {self.players[1].mention}\n"
                   f"Tienen 30 segundos para elegir una opción.",
            embed=None,
            view=game_view
        )
        
        if self.message.id in self.cog.active_games:
            del self.cog.active_games[self.message.id]

class RPS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}

    @app_commands.command(name="piedrapapeltijera", description="Únete o crea una partida de piedra, papel o tijera")
    async def ppt_slash(self, interaction: discord.Interaction):
        act_commands = get_specific_field(interaction.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
            return
        
        if "piedrapapeltijera" not in act_commands:
            await interaction.response.send_message("El comando no está activado en este servidor.")
            return
        
        for game_id, game_data in self.active_games.items():
            if len(game_data.players) < 2 and not game_data.started:
                game_data.players.append(interaction.user)
                
                embed = discord.Embed(
                    title="Partida de Piedra, Papel o Tijera",
                    description=f"**Anfitrión:** {game_data.host.mention}\n**Jugadores ({len(game_data.players)}/2):** {', '.join(p.mention for p in game_data.players)}",
                    color=discord.Color.green()
                )
                
                await game_data.message.edit(embed=embed, view=game_data)
                await interaction.response.send_message(f"Te has unido a una partida existente de Piedra, Papel o Tijera.", ephemeral=True)
                return
        
        view = RPSView(interaction.user, self)
        
        embed = discord.Embed(
            title="Partida de Piedra, Papel o Tijera",
            description=f"**Anfitrión:** {interaction.user.mention}\n**Jugadores (1/2):** {interaction.user.mention}",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed, view=view)
        
        message = await interaction.original_response()
        view.message = message
        self.active_games[message.id] = view
    
    @commands.command(name="piedrapapeltijera", description="Únete o crea una partida de piedra, papel o tijera")
    async def ppt_prefix(self, ctx):
        act_commands = get_specific_field(ctx.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if "piedrapapeltijera" not in act_commands:
            await ctx.reply("El comando no está activado en este servidor.")
            return
        
        for game_id, game_data in self.active_games.items():
            if len(game_data.players) < 2 and not game_data.started:
                game_data.players.append(ctx.author)
                
                embed = discord.Embed(
                    title="Partida de Piedra, Papel o Tijera",
                    description=f"**Anfitrión:** {game_data.host.mention}\n**Jugadores ({len(game_data.players)}/2):** {', '.join(p.mention for p in game_data.players)}",
                    color=discord.Color.green()
                )
                
                await game_data.message.edit(embed=embed, view=game_data)
                await ctx.send(f"{ctx.author.mention} se ha unido a una partida existente de Piedra, Papel o Tijera.", delete_after=3)
                return
        
        view = RPSView(ctx.author, self)
        
        embed = discord.Embed(
            title="Partida de Piedra, Papel o Tijera",
            description=f"**Anfitrión:** {ctx.author.mention}\n**Jugadores (1/2):** {ctx.author.mention}",
            color=discord.Color.green()
        )
        
        message = await ctx.send(embed=embed, view=view)
        view.message = message
        self.active_games[message.id] = view

async def setup(bot):
    await bot.add_cog(RPS(bot))