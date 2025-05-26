import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
from typing import List, Optional

from database.get import get_specific_field

class RussianRouletteView(discord.ui.View):
    def __init__(self, host: discord.Member):
        super().__init__(timeout=60)
        self.host = host
        self.players: List[discord.Member] = [host]
        self.started = False
        self.message: Optional[discord.Message] = None
        self.channel = None
        self.max_players = 6
    
    async def on_timeout(self):
        if not self.started:
            if len(self.players) == 1:
                await self.message.edit(
                    content="El tiempo para unirse a la partida ha expirado y no hay suficientes jugadores.",
                    view=None
                )
            elif len(self.players) > 1:
                self.started = True
                self.stop()
                await self.start_game_automatically()
    
    async def start_game_automatically(self):
        game = RussianRouletteGame(self.players, self.message, self.channel)
        await game.start_game()
    
    @discord.ui.button(label="Unirse a la partida", style=discord.ButtonStyle.primary)
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in self.players:
            await interaction.response.send_message("Ya estás en la partida.", ephemeral=True)
            return
        
        if len(self.players) >= self.max_players:
            await interaction.response.send_message("La partida está llena (máximo 6 jugadores).", ephemeral=True)
            return
        
        self.players.append(interaction.user)
        
        embed = discord.Embed(
            title="Partida de Ruleta Rusa",
            description=f"**Anfitrión:** {self.host.mention}\n**Jugadores ({len(self.players)}/{self.max_players}):** {', '.join(p.mention for p in self.players)}",
            color=discord.Color.red()
        )
        
        if len(self.players) < self.max_players:
            embed.set_footer(text="Esperando más jugadores... Se necesitan al menos 2 para iniciar.")
        else:
            embed.set_footer(text="Partida llena. El anfitrión puede iniciar cuando quiera.")
        
        await interaction.response.send_message(f"Te has unido a la partida de Ruleta Rusa de {self.host.display_name}.", ephemeral=True)
        await self.message.edit(embed=embed)
    
    @discord.ui.button(label="Salir de la partida", style=discord.ButtonStyle.secondary)
    async def leave_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user not in self.players:
            await interaction.response.send_message("No estás en la partida.", ephemeral=True)
            return
        
        if interaction.user == self.host:
            await interaction.response.send_message("Eres el anfitrión, no puedes salir de la partida.", ephemeral=True)
            return
        
        self.players.remove(interaction.user)
        
        embed = discord.Embed(
            title="Partida de Ruleta Rusa",
            description=f"**Anfitrión:** {self.host.mention}\n**Jugadores ({len(self.players)}/{self.max_players}):** {', '.join(p.mention for p in self.players)}",
            color=discord.Color.red()
        )
        
        if len(self.players) < self.max_players:
            embed.set_footer(text="Esperando más jugadores... Se necesitan al menos 2 para iniciar.")
        else:
            embed.set_footer(text="Partida llena. El anfitrión puede iniciar cuando quiera.")
        
        await interaction.response.send_message(f"Has salido de la partida de Ruleta Rusa.", ephemeral=True)
        await self.message.edit(embed=embed)
    
    @discord.ui.button(label="Iniciar partida", style=discord.ButtonStyle.danger)
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.host:
            await interaction.response.send_message("Solo el anfitrión puede iniciar la partida.", ephemeral=True)
            return
        
        if len(self.players) < 2:
            await interaction.response.send_message("Se necesitan al menos 2 jugadores para iniciar la partida.", ephemeral=True)
            return
        
        self.started = True
        self.stop()
        
        await interaction.response.send_message("Iniciando partida de Ruleta Rusa...", ephemeral=True)
        
        game = RussianRouletteGame(self.players, self.message, self.channel)
        await game.start_game()

class PlayerTurnView(discord.ui.View):
    def __init__(self, game, current_player: discord.Member):
        super().__init__(timeout=30)
        self.game = game
        self.current_player = current_player
        self.action_taken = False
        self.is_cancelled = False
    
    def cancel_view(self):
        self.is_cancelled = True
        self.stop()
    
    @discord.ui.button(label="🔫 Disparar", style=discord.ButtonStyle.danger)
    async def shoot_button(self, interaction: discord.Interaction, button: discord.ui.Button):        
        if self.is_cancelled:
            await interaction.response.send_message("Esta acción ya no es válida.", ephemeral=True)
            return
        
        if interaction.user != self.current_player:
            await interaction.response.send_message("No es tu turno.", ephemeral=True)
            return
        
        if self.action_taken:
            await interaction.response.send_message("Ya has disparado.", ephemeral=True)
            return
        
        self.action_taken = True
        self.stop()
        
        await interaction.response.send_message("Has decidido disparar. ¡Que la suerte esté contigo!", ephemeral=True)
    
    async def on_timeout(self):
        if not self.action_taken and not self.is_cancelled:
            self.action_taken = True

class RussianRouletteGame:
    def __init__(self, players: List[discord.Member], message: discord.Message, channel):
        self.original_players = players.copy()
        self.message = message
        self.channel = channel
        self.alive_players = players.copy()
        random.shuffle(self.alive_players)
        self.player_order = self.alive_players.copy()
        self.current_player_index = 0
        self.bullet_chamber = random.randint(1, 6)
        self.current_chamber = 1
        self.game_over = False
        self.round_number = 1
        self.current_view = None
    
    async def start_game(self):
        
        embed = discord.Embed(
            title="🔫 Ruleta Rusa - Iniciando",
            description=f"**Jugadores vivos:** {len(self.alive_players)}\n**Orden de juego:** {' → '.join(p.display_name for p in self.player_order)}",
            color=discord.Color.red()
        )
        embed.add_field(name="Estado del revólver", value="🔫 Cargado y listo (6 recámaras)", inline=False)
        embed.set_footer(text="El orden ha sido determinado aleatoriamente. ¡Que la suerte esté de su lado!")
        
        await self.message.edit(content=None, embed=embed, view=None)
        await asyncio.sleep(3)
        
        await self.play_game()
    
    async def play_game(self):
        
        while len(self.alive_players) > 1 and not self.game_over:
            
            if self.current_player_index >= len(self.player_order):
                self.current_player_index = 0
            
            current_player = self.player_order[self.current_player_index]
            
            if current_player not in self.alive_players:
                self.current_player_index += 1
                continue
            
            await self.player_turn(current_player)
            
            if self.game_over:
                break
            
            self.current_player_index += 1
        
        await self.end_game()
    
    async def player_turn(self, player: discord.Member):
        
        if self.current_view:
            self.current_view.cancel_view()
            self.current_view = None
        
        embed = discord.Embed(
            title=f"🔫 Ruleta Rusa - Ronda {self.round_number}",
            description=f"**Turno de:** {player.mention}\n**Jugadores vivos:** {len(self.alive_players)}\n**Recámara actual:** {self.current_chamber}/6",
            color=discord.Color.red()
        )
        embed.add_field(
            name="Jugadores restantes", 
            value=', '.join(p.display_name for p in self.alive_players), 
            inline=False
        )
        embed.set_footer(text=f"Es tu turno {player.display_name}. Presiona el botón para disparar.")
        
        self.current_view = PlayerTurnView(self, player)
        await self.message.edit(embed=embed, view=self.current_view)
        
        await self.current_view.wait()
        
        shot_result = await self.shoot(player, not self.current_view.action_taken)
        
        self.current_view = None
    
    async def shoot(self, player: discord.Member, timeout: bool = False):
        if self.game_over:
            return False
        
        if timeout:
            embed = discord.Embed(
                title=f"⏰ Tiempo agotado",
                description=f"{player.display_name} se quedó sin tiempo. El revólver dispara automáticamente...",
                color=discord.Color.orange()
            )
        else:
            embed = discord.Embed(
                title=f"🔫 {player.display_name} aprieta el gatillo...",
                description="💭 *Click... Click... Click...*",
                color=discord.Color.orange()
            )
        
        embed.set_thumbnail(url=player.display_avatar.url)
        await self.message.edit(embed=embed, view=None)
        await asyncio.sleep(3)
                
        if self.current_chamber == self.bullet_chamber:            
            embed = discord.Embed(
                title="💥 ¡BANG!",
                description=f"💀 **{player.display_name}** ha sido eliminado.\n*La bala estaba en la recámara {self.bullet_chamber}.*",
                color=discord.Color.dark_red()
            )
            embed.set_thumbnail(url=player.display_avatar.url)
            
            self.alive_players.remove(player)
            self.player_order = [p for p in self.player_order if p in self.alive_players]
                        
            if self.current_player_index >= len(self.player_order):
                self.current_player_index = 0
            
            if len(self.alive_players) == 1:
                self.game_over = True
            elif len(self.alive_players) > 1:
                self.bullet_chamber = random.randint(1, 6)
                self.current_chamber = 1
                self.round_number += 1
                embed.add_field(
                    name="Nueva ronda",
                    value=f"Se recarga el revólver para la ronda {self.round_number}.\nJugadores restantes: {len(self.alive_players)}",
                    inline=False
                )
            
            await self.message.edit(embed=embed, view=None)
            await asyncio.sleep(3)
            return True
        else:
            embed = discord.Embed(
                title="😅 ¡Click!",
                description=f"🍀 **{player.display_name}** ha sobrevivido.\n*La recámara {self.current_chamber} estaba vacía.*",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=player.display_avatar.url)
            self.current_chamber += 1
            
            await self.message.edit(embed=embed, view=None)
            await asyncio.sleep(3)
            return False
    
    async def end_game(self):
        if self.current_view:
            self.current_view.cancel_view()
            self.current_view = None
        
        if len(self.alive_players) == 1:
            winner = self.alive_players[0]
            embed = discord.Embed(
                title="🏆 ¡Tenemos un ganador!",
                description=f"🎉 **{winner.display_name}** es el último superviviente de la Ruleta Rusa.",
                color=discord.Color.gold()
            )
            embed.set_thumbnail(url=winner.display_avatar.url)
        else:
            embed = discord.Embed(
                title="😵 Fin del juego",
                description="No hay supervivientes. Todos han caído.",
                color=discord.Color.dark_grey()
            )
        
        eliminated_players = [p for p in self.original_players if p not in self.alive_players]
        if eliminated_players:
            eliminated_text = ", ".join([p.display_name for p in eliminated_players])
            embed.add_field(name="Jugadores eliminados", value=eliminated_text, inline=False)
        
        embed.add_field(name="Estadísticas", value=f"Rondas jugadas: {self.round_number}\nJugadores iniciales: {len(self.original_players)}", inline=False)
        
        await self.message.edit(embed=embed, view=None)

class RussianRoulette(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ruleta-rusa", aliases=["roulette"])
    async def ruleta_rusa_command(self, ctx):
        act_commands = get_specific_field(ctx.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if "ruletarusa" not in act_commands:
            await ctx.reply("El comando no está activado en este servidor.")
            return
        
        view = RussianRouletteView(ctx.author)
        view.channel = ctx.channel

        embed = discord.Embed(
            title="Partida de Ruleta Rusa",
            description=f"**Anfitrión:** {ctx.author.mention}\n**Jugadores (1/6):** {ctx.author.mention}",
            color=discord.Color.red()
        )
        embed.set_footer(text="Esperando más jugadores... Se necesitan al menos 2 para iniciar.")
        
        message = await ctx.send(embed=embed, view=view)
        view.message = message

    @app_commands.command(name="ruleta-rusa", description="Juega a la ruleta rusa multijugador. ¿Quién sobrevivirá?")
    async def ruleta_rusa_slash(self, interaction: discord.Interaction):
        act_commands = get_specific_field(interaction.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
            return
        
        if "ruletarusa" not in act_commands:
            await interaction.response.send_message("El comando no está activado en este servidor.")
            return
        
        view = RussianRouletteView(interaction.user)
        view.channel = interaction.channel

        embed = discord.Embed(
            title="Partida de Ruleta Rusa",
            description=f"**Anfitrión:** {interaction.user.mention}\n**Jugadores (1/6):** {interaction.user.mention}",
            color=discord.Color.red()
        )
        embed.set_footer(text="Esperando más jugadores... Se necesitan al menos 2 para iniciar.")
        
        await interaction.response.send_message(embed=embed, view=view)
        
        message = await interaction.original_response()
        view.message = message

async def setup(bot):
    await bot.add_cog(RussianRoulette(bot))