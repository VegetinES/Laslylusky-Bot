import discord
from discord import app_commands
from discord.ext import commands, tasks
import random
import asyncio
from typing import Dict, List, Tuple, Optional, Set
from database.get import get_specific_field
from database.minigames import update_blackjack_stats

class BlackjackView(discord.ui.View):
    def __init__(self, host: discord.Member):
        super().__init__(timeout=60)
        self.host = host
        self.players: List[discord.Member] = [host]
        self.started = False
        self.message: Optional[discord.Message] = None
        self.channel = None
        self.interaction = None
    
    async def on_timeout(self):
        if not self.started and self.message:
            await self.message.edit(
                content="El tiempo para unirse a la partida ha expirado y no hay suficientes jugadores.",
                view=None
            )
    
    @discord.ui.button(label="Unirse a la partida", style=discord.ButtonStyle.primary)
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in self.players:
            await interaction.response.send_message("Ya estás en la partida.", ephemeral=True)
            return
        
        self.players.append(interaction.user)
        
        embed = discord.Embed(
            title="Partida de Blackjack",
            description=f"**Anfitrión:** {self.host.mention}\n**Jugadores ({len(self.players)}):** {', '.join(p.mention for p in self.players)}",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(f"Te has unido a la partida de Blackjack de {self.host.display_name}.", ephemeral=True)
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
            title="Partida de Blackjack",
            description=f"**Anfitrión:** {self.host.mention}\n**Jugadores ({len(self.players)}):** {', '.join(p.mention for p in self.players)}",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(f"Has salido de la partida de Blackjack.", ephemeral=True)
        await self.message.edit(embed=embed)
    
    @discord.ui.button(label="Iniciar partida", style=discord.ButtonStyle.success)
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.host:
            await interaction.response.send_message("Solo el anfitrión puede iniciar la partida.", ephemeral=True)
            return
        
        if len(self.players) < 2:
            await interaction.response.send_message("Se necesitan al menos 2 jugadores para iniciar la partida.", ephemeral=True)
            return
        
        self.started = True
        self.stop()
        
        await interaction.response.send_message("Iniciando partida de Blackjack...", ephemeral=True)
        
        game = BlackjackGame(self.players, self.message, self.channel)
        await game.start_game()

class ConfirmView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=30)
        self.confirmed = False
    
    @discord.ui.button(label="Confirmar", style=discord.ButtonStyle.success)
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.confirmed = True
        self.stop()
        await interaction.response.edit_message(content="Acción confirmada", view=None)
    
    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.danger)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.confirmed = False
        self.stop()
        await interaction.response.edit_message(content="Acción cancelada", view=None)

class AceChoiceView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=30)
        self.choice = None
    
    @discord.ui.button(label="As vale 1", style=discord.ButtonStyle.primary)
    async def ace_one_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.choice = 1
        self.stop()
        await interaction.response.edit_message(content="Has elegido que el As valga 1.", view=None)
    
    @discord.ui.button(label="As vale 11", style=discord.ButtonStyle.success)
    async def ace_eleven_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.choice = 11
        self.stop()
        await interaction.response.edit_message(content="Has elegido que el As valga 11.", view=None)

class BlackjackGame:
    def __init__(self, players: List[discord.Member], message: discord.Message, channel):
        self.players = players
        self.message = message
        self.channel = channel
        self.deck = self.create_deck()
        self.player_hands: Dict[int, List[str]] = {}
        self.player_values: Dict[int, int] = {}
        self.player_status: Dict[int, str] = {}
        self.current_player_index = 0
        self.game_over = False
        self.turn_message = None
    
    def create_deck(self) -> List[str]:
        suits = ['♥', '♦', '♣', '♠']
        values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        deck = [f"{value}{suit}" for suit in suits for value in values]
        random.shuffle(deck)
        return deck
    
    def deal_card(self) -> str:
        return self.deck.pop()
    
    def calculate_hand_value(self, hand: List[str]) -> int:
        value = 0
        
        for card in hand:
            card_value = card[:-1]
            if card_value in ['J', 'Q', 'K']:
                value += 10
            elif card_value == 'A':
                value += 1
            else:
                value += int(card_value)
        
        return value
    
    async def handle_ace_choice(self, player: discord.Member, card: str) -> int:
        ace_view = AceChoiceView()
        ace_message = await self.channel.send(
            f"{player.mention}, has recibido un As ({card}). ¿Qué valor quieres que tenga?",
            view=ace_view,
            ephemeral=False
        )
        
        await ace_view.wait()
        
        try:
            await ace_message.delete()
        except:
            pass
        
        if ace_view.choice is None:
            return 11
        
        return ace_view.choice
    
    def format_hand(self, hand: List[str]) -> str:
        return ', '.join(hand)
    
    async def start_game(self):
        for player in self.players:
            self.player_hands[player.id] = []
            self.player_values[player.id] = 0
            self.player_status[player.id] = "esperando"
            
            for _ in range(2):
                card = self.deal_card()
                self.player_hands[player.id].append(card)
                if card[:-1] == 'A':
                    ace_value = await self.handle_ace_choice(player, card)
                    self.player_values[player.id] += ace_value
                else:
                    card_value = card[:-1]
                    if card_value in ['J', 'Q', 'K']:
                        self.player_values[player.id] += 10
                    else:
                        self.player_values[player.id] += int(card_value)
        
        await self.update_game_message()
        await self.play_turn()
    
    async def update_game_message(self):
        embed = discord.Embed(
            title="Partida de Blackjack en curso",
            color=discord.Color.gold()
        )
        
        for player in self.players:
            status_emoji = "⏳"
            status_text = "Esperando"
            
            if self.player_status[player.id] == "jugando":
                status_emoji = "🎮"
                status_text = "Jugando"
            elif self.player_status[player.id] == "plantado":
                status_emoji = "🛑"
                status_text = "Plantado"
            elif self.player_status[player.id] == "derrotado":
                status_emoji = "💥"
                status_text = "Derrotado"
            
            if self.game_over or self.player_status[player.id] == "derrotado":
                player_info = f"{status_emoji} Cartas: {len(self.player_hands[player.id])} - Valor: {self.player_values[player.id]}\n**Estado:** {status_text}"
            else:
                player_info = f"{status_emoji} Cartas: {len(self.player_hands[player.id])} - Valor: ???\n**Estado:** {status_text}"
            
            embed.add_field(name=f"{player.display_name}", value=player_info, inline=False)
        
        if not self.game_over and self.current_player_index < len(self.players):
            current_player = self.players[self.current_player_index]
            embed.set_footer(text=f"Turno de: {current_player.display_name}")
        
        await self.message.edit(content=None, embed=embed, view=None)
    
    async def play_turn(self):
        if self.game_over:
            await self.end_game()
            return
        
        active_players = [p for p in self.players if self.player_status[p.id] != "derrotado" and self.player_status[p.id] != "plantado"]
        if not active_players:
            await self.end_game()
            return
        
        current_player = self.players[self.current_player_index]
        
        if self.player_status[current_player.id] == "plantado" or self.player_status[current_player.id] == "derrotado":
            self.next_player()
            await self.play_turn()
            return
        
        self.player_status[current_player.id] = "jugando"
        await self.update_game_message()
        
        if self.turn_message:
            try:
                await self.turn_message.delete()
            except:
                pass
        
        turn_view = PlayerTurnView(self, current_player)
        
        self.turn_message = await self.channel.send(
            f"{current_player.mention} es tu turno, para ver tus cartas dale al botón `Ver mis cartas`",
            view=turn_view
        )
        
        await turn_view.wait()
        
        if not turn_view.action_taken:
            self.player_status[current_player.id] = "plantado"
        
        await self.update_game_message()
        
        self.next_player()
        
        await self.play_turn()
    
    def next_player(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        if self.current_player_index == 0:
            self.game_over = True
    
    async def hit(self, player: discord.Member) -> bool:
        new_card = self.deal_card()
        self.player_hands[player.id].append(new_card)
        
        if new_card[:-1] == 'A':
            ace_value = await self.handle_ace_choice(player, new_card)
            self.player_values[player.id] += ace_value
        else:
            card_value = new_card[:-1]
            if card_value in ['J', 'Q', 'K']:
                self.player_values[player.id] += 10
            else:
                self.player_values[player.id] += int(card_value)
        
        if self.player_values[player.id] > 21:
            self.player_status[player.id] = "derrotado"
            return True
        
        return False
    
    async def stand(self, player: discord.Member):
        self.player_status[player.id] = "plantado"
    
    async def end_game(self):
        if self.turn_message:
            try:
                await self.turn_message.delete()
            except:
                pass
        
        max_value = 0
        for player_id, status in self.player_status.items():
            if status != "derrotado" and self.player_values[player_id] <= 21 and self.player_values[player_id] > max_value:
                max_value = self.player_values[player_id]
        
        winners = []
        for player in self.players:
            if self.player_status[player.id] != "derrotado" and self.player_values[player.id] == max_value:
                winners.append(player)
        
        embed = discord.Embed(
            title="Fin de la partida de Blackjack",
            color=discord.Color.blue()
        )
        
        for player in self.players:
            status_text = "Plantado"
            if self.player_status[player.id] == "derrotado":
                status_text = "Pasado de 21"
            
            result = f"**Valor final:** {self.player_values[player.id]} - **Cartas:** {self.format_hand(self.player_hands[player.id])}\n**Estado:** {status_text}"
            
            if player in winners:
                result = f"🏆 {result}"
            
            embed.add_field(name=player.display_name, value=result, inline=False)
        
        if winners:
            winner_text = ", ".join([w.mention for w in winners])
            embed.description = f"**Ganadores:** {winner_text} con {max_value} puntos."
        else:
            embed.description = "No hay ganadores. Todos se han pasado de 21."
        
        await self.message.edit(content=None, embed=embed, view=None)
        
        for player in self.players:
            result = "loss"
            points = 0
            
            if player in winners:
                result = "win"
                points = self.player_values[player.id] + (len(self.players) * 5)
                if self.player_values[player.id] == 21 and len(self.player_hands[player.id]) == 2:
                    points += 20
            elif self.player_status[player.id] == "derrotado":
                result = "bust"
            
            game_data = {
                'result': result,
                'final_value': self.player_values[player.id],
                'cards': self.player_hands[player.id],
                'points': points,
                'num_cards': len(self.player_hands[player.id])
            }
            
            update_blackjack_stats(player.id, game_data)

class PlayerTurnView(discord.ui.View):
    def __init__(self, game: BlackjackGame, player: discord.Member):
        super().__init__(timeout=60)
        self.game = game
        self.player = player
        self.action_taken = False
    
    @discord.ui.button(label="Pedir carta", style=discord.ButtonStyle.primary)
    async def hit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.player:
            await interaction.response.send_message("No es tu turno.", ephemeral=True)
            return
        
        if self.game.player_status[self.player.id] != "jugando":
            await interaction.response.send_message("Ya no puedes realizar esta acción.", ephemeral=True)
            return
            
        await interaction.response.send_message("Has pedido una carta.", ephemeral=True)
        
        self.action_taken = True
        busted = await self.game.hit(self.player)
        
        if busted:
            await interaction.followup.send(f"¡Te has pasado de 21! Valor final: {self.game.player_values[self.player.id]}", ephemeral=True)
            self.stop()
        else:
            await interaction.followup.send(
                f"Tu mano ahora: {self.game.format_hand(self.game.player_hands[self.player.id])}\n"
                f"Valor actual: {self.game.player_values[self.player.id]}",
                ephemeral=True
            )
    
    @discord.ui.button(label="Plantarse", style=discord.ButtonStyle.secondary)
    async def stand_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.player:
            await interaction.response.send_message("No es tu turno.", ephemeral=True)
            return
            
        if self.game.player_status[self.player.id] != "jugando":
            await interaction.response.send_message("Ya no puedes realizar esta acción.", ephemeral=True)
            return
            
        await interaction.response.send_message(f"Te has plantado con un valor de {self.game.player_values[self.player.id]}.", ephemeral=True)
        
        self.action_taken = True
        await self.game.stand(self.player)
        
        self.stop()
    
    @discord.ui.button(label="Ver mis cartas", style=discord.ButtonStyle.success)
    async def view_cards_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.player:
            await interaction.response.send_message("No es tu turno.", ephemeral=True)
            return
        
        hand = self.game.player_hands[self.player.id]
        value = self.game.player_values[self.player.id]
        
        await interaction.response.send_message(
            f"Tus cartas: {self.game.format_hand(hand)}\n"
            f"Valor total: {value}",
            ephemeral=True
        )

class Blackjack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="blackjack", description="Inicia una partida de Blackjack")
    async def blackjack_slash(self, interaction: discord.Interaction):
        view = BlackjackView(interaction.user)
        view.channel = interaction.channel

        act_commands = get_specific_field(interaction.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
            return
        
        if "blackjack" not in act_commands:
            await interaction.response.send_message("El comando no está activado en este servidor.")
            return
        
        embed = discord.Embed(
            title="Partida de Blackjack",
            description=f"**Anfitrión:** {interaction.user.mention}\n**Jugadores (1):** {interaction.user.mention}",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed, view=view)
        
        message = await interaction.original_response()
        view.message = message
    
    @commands.command(name="blackjack", aliases=["bj"])
    async def blackjack_prefix(self, ctx):
        view = BlackjackView(ctx.author)
        view.channel = ctx.channel

        act_commands = get_specific_field(ctx.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if "blackjack" not in act_commands:
            await ctx.send("El comando no está activado en este servidor.")
            return
        
        embed = discord.Embed(
            title="Partida de Blackjack",
            description=f"**Anfitrión:** {ctx.author.mention}\n**Jugadores (1):** {ctx.author.mention}",
            color=discord.Color.green()
        )
        
        message = await ctx.send(embed=embed, view=view)
        view.message = message

async def setup(bot):
    await bot.add_cog(Blackjack(bot))