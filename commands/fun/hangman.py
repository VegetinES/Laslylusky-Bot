import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import time
import random
import unicodedata
import string
from datetime import datetime, timedelta
from database.get import get_specific_field
from database.minigames import get_user_stats, update_hangman_stats

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

class HangmanGame:
    def __init__(self, players):
        self.players = players.copy()
        self.round_number = 0
        self.current_host_index = 0
        self.current_word = None
        self.word_without_accents = None
        self.guessed_letters = set()
        self.wrong_guesses = 0
        self.max_wrong_guesses = 6
        self.status = "waiting_word"
        self.start_time = datetime.now()
        self.round_start_time = None
        self.current_display = ""
        self.scores = {player.id: 0 for player in players}
        self.rounds_completed = 0
        self.max_rounds = len(players)
        self.guessing_players = []
        self.current_guesser_index = 0

    def start_new_round(self):
        self.round_number += 1
        self.rounds_completed += 1
        self.current_word = None
        self.word_without_accents = None
        self.guessed_letters = set()
        self.wrong_guesses = 0
        self.status = "waiting_word"
        self.round_start_time = datetime.now()
        self.current_display = ""
        self.guessing_players = [p for p in self.players if p != self.get_current_host()]
        self.current_guesser_index = 0

    def get_current_host(self):
        if self.current_host_index < len(self.players):
            return self.players[self.current_host_index]
        return None

    def get_current_guesser(self):
        if self.status == "active" and self.guessing_players:
            return self.guessing_players[self.current_guesser_index % len(self.guessing_players)]
        return None

    def next_guesser(self):
        if self.guessing_players:
            self.current_guesser_index = (self.current_guesser_index + 1) % len(self.guessing_players)

    def next_round(self):
        self.current_host_index += 1
        if self.current_host_index >= len(self.players):
            self.status = "finished"
            return False
        self.start_new_round()
        return True

    def set_word(self, word):
        self.current_word = word.lower()
        self.word_without_accents = remove_accents(self.current_word.lower())
        self.status = "active"
        self.current_display = self.update_display()
        self.round_start_time = datetime.now()

    def update_display(self):
        if not self.current_word:
            return ""
        display = []
        for char in self.current_word:
            if char == ' ':
                display.append('-')
            elif char in '.,!?;:':
                display.append(char)
            elif remove_accents(char) in self.guessed_letters:
                display.append(char)
            else:
                display.append('*')
        return ' '.join(display)

    def guess_letter(self, letter, player):
        if self.status != "active":
            return False, "game_not_active"
        
        if player != self.get_current_guesser():
            return False, "not_your_turn"

        letter = letter.lower().strip()
        
        if remove_accents(letter) in self.guessed_letters:
            return False, "repeat"
        
        self.guessed_letters.add(remove_accents(letter))
        
        if remove_accents(letter) in self.word_without_accents:
            self.current_display = self.update_display()
            if '*' not in self.current_display:
                self.status = "round_won"
                self.scores[player.id] += 100
                host = self.get_current_host()
                if host:
                    self.scores[host.id] += 50
                return True, "win"
            return True, "correct"
        else:
            self.wrong_guesses += 1
            if self.wrong_guesses >= self.max_wrong_guesses:
                self.status = "round_lost"
                host = self.get_current_host()
                if host:
                    self.scores[host.id] += 75
                return False, "lose"
            self.next_guesser()
            return False, "wrong"

    def guess_word(self, guessed_word, player):
        if self.status != "active":
            return False, "game_not_active"
        
        if player != self.get_current_guesser():
            return False, "not_your_turn"

        guessed_word = guessed_word.lower().strip()
        if remove_accents(guessed_word) == self.word_without_accents:
            self.status = "round_won"
            self.scores[player.id] += 150
            host = self.get_current_host()
            if host:
                self.scores[host.id] += 50
            
            for char in self.word_without_accents:
                if char not in ' .,!?;:':
                    self.guessed_letters.add(char)
            
            self.current_display = self.update_display()
            return True, "win"
        else:
            self.wrong_guesses += 1
            if self.wrong_guesses >= self.max_wrong_guesses:
                self.status = "round_lost"
                host = self.get_current_host()
                if host:
                    self.scores[host.id] += 75
                return False, "lose"
            self.next_guesser()
            return False, "wrong"

    def get_hangman_display(self):
        stages = [
            '''```
  +---+
  |   |
      |
      |
      |
      |
=========```''',
            '''```
  +---+
  |   |
  O   |
      |
      |
      |
=========```''',
            '''```
  +---+
  |   |
  O   |
  |   |
      |
      |
=========```''',
            '''```
  +---+
  |   |
  O   |
 /|   |
      |
      |
=========```''',
            '''```
  +---+
  |   |
  O   |
 /|\\  |
      |
      |
=========```''',
            '''```
  +---+
  |   |
  O   |
 /|\\  |
 /    |
      |
=========```''',
            '''```
  +---+
  |   |
  O   |
 /|\\  |
 / \\  |
      |
=========```'''
        ]
        return stages[min(self.wrong_guesses, len(stages) - 1)]

    def get_winner(self):
        if not self.scores:
            return None
        max_score = max(self.scores.values())
        winners = [player for player in self.players if self.scores[player.id] == max_score]
        return winners[0] if len(winners) == 1 else winners

    def get_leaderboard(self):
        sorted_scores = sorted(self.scores.items(), key=lambda x: x[1], reverse=True)
        return [(player_id, score) for player_id, score in sorted_scores]

class HangmanLobbyView(discord.ui.View):
    def __init__(self, host, cog):
        super().__init__(timeout=300)
        self.host = host
        self.players = [host]
        self.started = False
        self.message = None
        self.cog = cog
    
    async def on_timeout(self):
        if not self.started and self.message:
            await self.message.edit(
                content="El tiempo para unirse a la partida ha expirado.",
                view=None
            )
        
        if self.message and self.message.id in self.cog.active_games:
            del self.cog.active_games[self.message.id]
    
    @discord.ui.button(label="Unirse", style=discord.ButtonStyle.primary, emoji="➕")
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in self.players:
            await interaction.response.send_message("Ya estás en la partida.", ephemeral=True)
            return
        
        if len(self.players) >= 8:
            await interaction.response.send_message("La partida ya está llena (máximo 8 jugadores).", ephemeral=True)
            return
        
        self.players.append(interaction.user)
        await self.update_lobby_message(interaction)
    
    @discord.ui.button(label="Salir", style=discord.ButtonStyle.secondary, emoji="➖")
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
        
        await self.update_lobby_message(interaction)
    
    @discord.ui.button(label="Iniciar", style=discord.ButtonStyle.success, emoji="🎮")
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.host:
            await interaction.response.send_message("Solo el anfitrión puede iniciar la partida.", ephemeral=True)
            return
        
        if len(self.players) < 2:
            await interaction.response.send_message("Se necesitan al menos 2 jugadores para iniciar.", ephemeral=True)
            return
        
        self.started = True
        self.stop()
        
        await interaction.response.send_message("¡Iniciando partida de Ahorcado!", ephemeral=True)
        await self.start_game()

    async def update_lobby_message(self, interaction):
        embed = discord.Embed(
            title="🎮 Sala de Ahorcado",
            description=f"**Anfitrión:** {self.host.mention}\n**Jugadores ({len(self.players)}/8):**\n" + 
                       "\n".join([f"• {p.mention}" for p in self.players]),
            color=discord.Color.blue()
        )
        embed.add_field(
            name="📋 Cómo jugar",
            value="• Cada jugador pondrá una palabra por turno\n• Los demás intentan adivinarla\n• Gana puntos quien adivine primero\n• ¡El que más puntos tenga al final gana!",
            inline=False
        )
        embed.set_footer(text=f"Rondas totales: {len(self.players)} | Mínimo 2 jugadores")
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def start_game(self):
        game = HangmanGame(self.players)
        game_view = HangmanGameView(game, self.cog)
        game_view.message = self.message
        
        game.start_new_round()
        await game_view.update_game_message()
        
        if self.message.id in self.cog.active_games:
            self.cog.active_games[self.message.id] = game_view

class HangmanGameView(discord.ui.View):
    def __init__(self, game, cog):
        super().__init__(timeout=None)
        self.game = game
        self.message = None
        self.cog = cog
    
    async def update_game_message(self, interaction=None):
        embed = discord.Embed(title="🎮 Juego del Ahorcado", color=discord.Color.blue())
        
        if self.game.status == "waiting_word":
            current_host = self.game.get_current_host()
            embed.description = f"**Ronda {self.game.round_number}/{self.game.max_rounds}**\n\n🎯 {current_host.mention} debe establecer la palabra/frase"
            embed.add_field(
                name="👥 Jugadores",
                value="\n".join([f"• {p.mention}" for p in self.game.players]),
                inline=True
            )
            
        elif self.game.status == "active":
            embed.description = self.game.get_hangman_display()
            embed.add_field(name="🔤 Palabra/Frase", value=f"```\n{self.game.current_display}\n```", inline=False)
            embed.add_field(name="📝 Letras usadas", value=', '.join(sorted(self.game.guessed_letters)) if self.game.guessed_letters else "Ninguna", inline=True)
            embed.add_field(name="❌ Errores", value=f"{self.game.wrong_guesses}/{self.game.max_wrong_guesses}", inline=True)
            
            current_guesser = self.game.get_current_guesser()
            current_host = self.game.get_current_host()
            embed.add_field(name="🎯 Turno actual", value=f"{current_guesser.mention if current_guesser else 'Nadie'}", inline=True)
            embed.add_field(name="📖 Palabra de", value=f"{current_host.mention if current_host else 'Nadie'}", inline=True)
            
        elif self.game.status in ["round_won", "round_lost"]:
            if self.game.status == "round_won":
                winner = self.game.get_current_guesser()
                embed.title = "🎉 ¡Ronda Ganada!"
                embed.description = f"¡{winner.mention if winner else 'Alguien'} adivinó la palabra!"
                embed.color = discord.Color.green()
            else:
                embed.title = "💀 Ronda Perdida"
                embed.description = "Nadie logró adivinar la palabra."
                embed.color = discord.Color.red()
            
            embed.add_field(name="🔤 La palabra era", value=f"**{self.game.current_word}**", inline=False)
            
        elif self.game.status == "finished":
            winners = self.game.get_winner()
            if isinstance(winners, list):
                embed.title = "🏆 ¡Empate!"
                embed.description = f"¡Empate entre: {', '.join([w.mention for w in winners])}!"
            else:
                embed.title = "🏆 ¡Partida Terminada!"
                embed.description = f"¡{winners.mention} ha ganado la partida!"
            embed.color = discord.Color.gold()
            self.clear_items()
        
        if self.game.status != "waiting_word":
            leaderboard = self.game.get_leaderboard()
            scores_text = []
            for i, (player_id, score) in enumerate(leaderboard):
                player = next((p for p in self.game.players if p.id == player_id), None)
                if player:
                    medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "🔸"
                    scores_text.append(f"{medal} {player.mention}: {score} pts")
            
            embed.add_field(
                name="📊 Puntuación",
                value="\n".join(scores_text) if scores_text else "Sin puntuaciones",
                inline=False
            )
        
        content = ""
        if self.game.status == "waiting_word":
            content = f"🎯 {self.game.get_current_host().mention}, ¡establece tu palabra/frase!"
        elif self.game.status == "active":
            content = f"🎯 Turno de {self.game.get_current_guesser().mention}"
        elif self.game.status in ["round_won", "round_lost"] and self.game.current_host_index + 1 < len(self.game.players):
            content = "⏳ Preparando siguiente ronda..."
        
        if interaction:
            await interaction.response.edit_message(content=content, embed=embed, view=self)
        elif self.message:
            await self.message.edit(content=content, embed=embed, view=self)
        
        if self.game.status in ["round_won", "round_lost"] and self.game.status != "finished":
            await asyncio.sleep(3)
            if self.game.next_round():
                await self.update_game_message()
            else:
                self.game.status = "finished"
                await self.update_game_message()
    
    @discord.ui.button(label="Establecer Palabra", style=discord.ButtonStyle.primary, emoji="📝")
    async def set_word_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.game.status != "waiting_word":
            await interaction.response.send_message("No es momento de establecer palabras.", ephemeral=True)
            return
        
        current_host = self.game.get_current_host()
        if interaction.user != current_host:
            await interaction.response.send_message("No es tu turno para establecer la palabra.", ephemeral=True)
            return
        
        modal = SetWordModal(self)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Adivinar Letra", style=discord.ButtonStyle.secondary, emoji="🔤")
    async def guess_letter_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.game.status != "active":
            await interaction.response.send_message("El juego no está activo.", ephemeral=True)
            return
        
        current_guesser = self.game.get_current_guesser()
        if interaction.user != current_guesser:
            await interaction.response.send_message("No es tu turno para adivinar.", ephemeral=True)
            return
        
        modal = GuessLetterModal(self)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Adivinar Palabra", style=discord.ButtonStyle.secondary, emoji="💭")
    async def guess_word_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.game.status != "active":
            await interaction.response.send_message("El juego no está activo.", ephemeral=True)
            return
        
        current_guesser = self.game.get_current_guesser()
        if interaction.user != current_guesser:
            await interaction.response.send_message("No es tu turno para adivinar.", ephemeral=True)
            return
        
        modal = GuessWordModal(self)
        await interaction.response.send_modal(modal)

class SetWordModal(discord.ui.Modal, title="Establecer Palabra/Frase"):
    word_input = discord.ui.TextInput(
        label="Palabra o frase para adivinar",
        placeholder="Escribe aquí la palabra o frase...",
        min_length=2,
        max_length=100
    )
    
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view
    
    async def on_submit(self, interaction: discord.Interaction):
        word = self.word_input.value.strip()
        if len(word) < 2:
            await interaction.response.send_message("La palabra debe tener al menos 2 caracteres.", ephemeral=True)
            return
        
        self.game_view.game.set_word(word)
        await interaction.response.send_message("¡Palabra establecida! Los demás pueden empezar a adivinar.", ephemeral=True)
        await self.game_view.update_game_message()

class GuessLetterModal(discord.ui.Modal, title="Adivinar Letra"):
    letter_input = discord.ui.TextInput(
        label="Ingresa una letra",
        placeholder="a",
        min_length=1,
        max_length=1
    )
    
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view
    
    async def on_submit(self, interaction: discord.Interaction):
        letter = self.letter_input.value.strip().lower()
        
        if not letter.isalpha():
            await interaction.response.send_message("Debes ingresar una letra válida.", ephemeral=True)
            return
        
        success, result = self.game_view.game.guess_letter(letter, interaction.user)
        
        if result == "repeat":
            await interaction.response.send_message("Esa letra ya fue usada.", ephemeral=True)
            return
        elif result == "not_your_turn":
            await interaction.response.send_message("No es tu turno.", ephemeral=True)
            return
        
        message = ""
        if result == "correct":
            message = "¡Letra correcta!"
        elif result == "wrong":
            message = "Letra incorrecta."
        elif result == "win":
            message = "¡Has adivinado la palabra!"
        elif result == "lose":
            message = "Se acabaron los intentos."
        
        await interaction.response.send_message(message, ephemeral=True)
        await self.game_view.update_game_message()

class GuessWordModal(discord.ui.Modal, title="Adivinar Palabra/Frase"):
    word_input = discord.ui.TextInput(
        label="Palabra o frase completa",
        placeholder="Escribe aquí tu respuesta...",
        min_length=1,
        max_length=100
    )
    
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view
    
    async def on_submit(self, interaction: discord.Interaction):
        word = self.word_input.value.strip()
        
        success, result = self.game_view.game.guess_word(word, interaction.user)
        
        if result == "not_your_turn":
            await interaction.response.send_message("No es tu turno.", ephemeral=True)
            return
        
        message = ""
        if result == "win":
            message = "¡Correcto! Has adivinado la palabra/frase."
        elif result == "wrong":
            message = "Incorrecto."
        elif result == "lose":
            message = "Incorrecto. Se acabaron los intentos."
        
        await interaction.response.send_message(message, ephemeral=True)
        await self.game_view.update_game_message()

class Hangman(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}
    
    @commands.command(name="ahorcado")
    async def hangman_command(self, ctx):
        act_commands = get_specific_field(ctx.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if "ahorcado" not in act_commands:
            await ctx.reply("El comando no está activado en este servidor.")
            return
        
        view = HangmanLobbyView(ctx.author, self)
        
        embed = discord.Embed(
            title="🎮 Sala de Ahorcado",
            description=f"**Anfitrión:** {ctx.author.mention}\n**Jugadores (1/8):**\n• {ctx.author.mention}",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="📋 Cómo jugar",
            value="• Cada jugador pondrá una palabra por turno\n• Los demás intentan adivinarla\n• Gana puntos quien adivine primero\n• ¡El que más puntos tenga al final gana!",
            inline=False
        )
        embed.set_footer(text="Rondas totales: 1 | Mínimo 2 jugadores")
        
        message = await ctx.send(embed=embed, view=view)
        view.message = message
        self.active_games[message.id] = view
    
    @app_commands.command(name="ahorcado", description="Crear o unirse a una partida de ahorcado")
    async def hangman_slash(self, interaction: discord.Interaction):
        act_commands = get_specific_field(interaction.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
            return
        
        if "ahorcado" not in act_commands:
            await interaction.response.send_message("El comando no está activado en este servidor.")
            return
        
        view = HangmanLobbyView(interaction.user, self)
        
        embed = discord.Embed(
            title="🎮 Sala de Ahorcado",
            description=f"**Anfitrión:** {interaction.user.mention}\n**Jugadores (1/8):**\n• {interaction.user.mention}",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="📋 Cómo jugar",
            value="• Cada jugador pondrá una palabra por turno\n• Los demás intentan adivinarla\n• Gana puntos quien adivine primero\n• ¡El que más puntos tenga al final gana!",
            inline=False
        )
        embed.set_footer(text="Rondas totales: 1 | Mínimo 2 jugadores")
        
        await interaction.response.send_message(embed=embed, view=view)
        
        message = await interaction.original_response()
        view.message = message
        self.active_games[message.id] = view

async def setup(bot):
    await bot.add_cog(Hangman(bot))