import discord
from discord import app_commands
from discord.ext import commands, tasks
import random
from collections import deque
import asyncio
from datetime import datetime, timedelta
from database.get import get_specific_field
from database.minigames import get_user_stats, update_minesweeper_stats

class Minesweeper(commands.Cog):
   def __init__(self, bot):
       self.bot = bot
       self.active_games = {}
       self.last_interaction = {}
       self.game_messages = {}
       self.check_inactive_games.start()

   def cog_unload(self):
       self.check_inactive_games.cancel()

   @tasks.loop(seconds=30)
   async def check_inactive_games(self):
       current_time = datetime.now()
       users_to_end = []
       
       for user_id, last_time in list(self.last_interaction.items()):
           if current_time - last_time > timedelta(minutes=5):
               if user_id in self.active_games and not self.active_games[user_id]['game_over']:
                   users_to_end.append(user_id)
       
       for user_id in users_to_end:
           try:
               user = await self.bot.fetch_user(user_id)
               game = self.active_games[user_id]
               game['game_over'] = True
               
               if user_id in self.game_messages:
                   try:
                       embed = discord.Embed(
                           title=f"Buscaminas de {user.name} - Partida terminada por inactividad",
                           description=self.format_board_display(game),
                           color=0xFF0000
                       )
                       await self.game_messages[user_id].edit(embed=embed)
                       del self.game_messages[user_id]
                   except:
                       pass
               
               self.save_game_stats(user_id, game, 'abandoned')
               
               del self.active_games[user_id]
               del self.last_interaction[user_id]
           except Exception as e:
               print(f"Error al terminar juego inactivo: {e}")
   
   @check_inactive_games.before_loop
   async def before_check_inactive_games(self):
       await self.bot.wait_until_ready()

   @commands.Cog.listener()
   async def on_message(self, message):
       if message.author.bot:
           return
           
       user_id = message.author.id
       
       if user_id not in self.active_games:
           return
           
       game = self.active_games[user_id]
       
       if game['game_over']:
           return
           
       content = message.content.strip()
       
       try:
           parts = content.split()
           
           if len(parts) < 2:
               return
               
           try:
               x = int(parts[0])
               y = int(parts[1])
           except ValueError:
               return
               
           is_flag = len(parts) > 2 and "flag" in parts
           
           await message.delete()
           
           self.last_interaction[user_id] = datetime.now()
           game['show_instructions'] = False
           
           if not (1 <= x <= game['size'] and 1 <= y <= game['size']):
               return
           
           x_internal = x - 1
           y_internal = y - 1
           
           if is_flag:
               if (x_internal, y_internal) in game['flags']:
                   game['flags'].remove((x_internal, y_internal))
                   game['visible_board'][y_internal][x_internal] = '⚪'
                   game['flags_placed'] -= 1
               else:
                   if game['visible_board'][y_internal][x_internal] != '⚪':
                       return
                       
                   game['flags'].append((x_internal, y_internal))
                   game['visible_board'][y_internal][x_internal] = '<:minesweeperflag:1376450252860559430>'
                   game['flags_placed'] += 1
                   
                   if game['board'][y_internal][x_internal] == -1:
                       game['correct_flags'] += 1
               
               embed = discord.Embed(
                   title=f"Buscaminas de {message.author.name}",
                   description=self.format_board_display(game),
                   color=0xF764
               )
               
               if user_id in self.game_messages:
                   await self.game_messages[user_id].edit(embed=embed)
           else:
               if (x_internal, y_internal) in game['flags']:
                   return
               
               if game['visible_board'][y_internal][x_internal] != '⚪':
                   return
               
               if game['board'][y_internal][x_internal] == -1:
                   game['game_over'] = True
                   game['end_time'] = datetime.now()
                   game['visible_board'][y_internal][x_internal] = '💣'
                   
                   for row_idx, row in enumerate(game['board']):
                       for col_idx, cell in enumerate(row):
                           if cell == -1 and game['visible_board'][row_idx][col_idx] != '💣':
                               game['visible_board'][row_idx][col_idx] = '💣'
                   
                   embed = discord.Embed(
                       title=f"Buscaminas de {message.author.name} - ¡BOOM! Juego terminado",
                       description=self.format_board_display(game),
                       color=0xFF0000
                   )
                   
                   if user_id in self.game_messages:
                       await self.game_messages[user_id].edit(embed=embed)
                       del self.game_messages[user_id]
                   
                   self.save_game_stats(user_id, game, 'loss')
                   
                   if user_id in self.last_interaction:
                       del self.last_interaction[user_id]
               else:
                   self.reveal_cell(game['board'], game['visible_board'], x_internal, y_internal, game)
                   
                   if self.check_win(game['board'], game['visible_board'], game['mines']):
                       game['game_over'] = True
                       game['end_time'] = datetime.now()
                       
                       for row_idx, row in enumerate(game['board']):
                           for col_idx, cell in enumerate(row):
                               if cell == -1:
                                   game['visible_board'][row_idx][col_idx] = '<:minesweeperflag:1376450252860559430>'
                                   if (row_idx, col_idx) not in game['flags']:
                                       game['flags'].append((row_idx, col_idx))
                                       game['flags_placed'] += 1
                                       game['correct_flags'] += 1
                       
                       game_time = (game['end_time'] - game['start_time']).total_seconds()
                       difficulty_multiplier = 1 if game['size'] == 6 else (2 if game['size'] == 8 else 3)
                       time_bonus = max(0, 300 - game_time) / 10
                       points = game['mines'] * difficulty_multiplier + time_bonus
                       
                       embed = discord.Embed(
                           title=f"Buscaminas de {message.author.name} - ¡Victoria!",
                           description=self.format_board_display(game),
                           color=0x00FF00
                       )
                       
                       embed.add_field(name="Dificultad", value=game['difficulty'], inline=True)
                       embed.add_field(name="Tiempo", value=f"{game_time:.1f} segundos", inline=True)
                       embed.add_field(name="Puntos ganados", value=f"{points:.0f}", inline=True)
                       
                       if user_id in self.game_messages:
                           await self.game_messages[user_id].edit(embed=embed)
                           del self.game_messages[user_id]
                       
                       self.save_game_stats(user_id, game, 'win', points)
                       
                       if user_id in self.last_interaction:
                           del self.last_interaction[user_id]
                   else:
                       embed = discord.Embed(
                           title=f"Buscaminas de {message.author.name}",
                           description=self.format_board_display(game),
                           color=0xF764
                       )
                       
                       if user_id in self.game_messages:
                           await self.game_messages[user_id].edit(embed=embed)
                       
       except Exception as e:
           print(f"Error procesando movimiento: {e}")

   @app_commands.command(name="buscaminas", description="Inicia un juego de buscaminas")
   @app_commands.choices(dificultad=[
       app_commands.Choice(name="Fácil", value="facil"),
       app_commands.Choice(name="Normal", value="normal"),
       app_commands.Choice(name="Difícil", value="dificil")
   ])
   async def buscaminas(self, interaction: discord.Interaction, dificultad: app_commands.Choice[str]):
       act_commands = get_specific_field(interaction.guild.id, "act_cmd")
       if act_commands is None:
           embed = discord.Embed(
               title="<:No:825734196256440340> Error de Configuración",
               description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
               color=discord.Color.red()
           )
           await interaction.response.send_message(embed=embed)
           return
       
       if "buscaminas" not in act_commands:
           await interaction.response.send_message("El comando no está activado en este servidor.")
           return
       
       user_id = interaction.user.id
       username = interaction.user.name
       
       if user_id in self.active_games and not self.active_games[user_id]['game_over']:
           view = GameManagementView(self, user_id)
           await interaction.response.send_message(
               "Ya tienes una partida de buscaminas en curso. ¿Qué deseas hacer?",
               view=view,
               ephemeral=True
           )
           return

       if dificultad.value == "facil":
           size = 6
           mines = 6
           difficulty_name = "Fácil"
       elif dificultad.value == "normal":
           size = 8
           mines = random.randint(10, 12)
           difficulty_name = "Normal"
       else:
           size = 10
           mines = random.randint(15, 20)
           difficulty_name = "Difícil"

       board = self.generate_board(size, mines)
       
       visible_board = [['⚪' for _ in range(size)] for _ in range(size)]
       
       self.active_games[user_id] = {
           'board': board,
           'visible_board': visible_board,
           'size': size,
           'mines': mines,
           'flags': [],
           'game_over': False,
           'start_time': datetime.now(),
           'end_time': None,
           'difficulty': difficulty_name,
           'cells_uncovered': 0,
           'flags_placed': 0,
           'correct_flags': 0,
           'show_instructions': True,
           'last_channel_id': interaction.channel_id
       }
       
       self.last_interaction[user_id] = datetime.now()
       
       embed = discord.Embed(
           title=f"Buscaminas de {username}",
           description=self.format_board_display(self.active_games[user_id]),
           color=0xF764
       )
       
       await interaction.response.send_message(embed=embed)
       
       message = await interaction.original_response()
       self.game_messages[user_id] = message

   def generate_board(self, size, mines):
       board = [[0 for _ in range(size)] for _ in range(size)]
       
       mines_placed = 0
       while mines_placed < mines:
           x = random.randint(0, size - 1)
           y = random.randint(0, size - 1)
           
           if board[y][x] != -1:
               board[y][x] = -1
               mines_placed += 1
               
               for dx in [-1, 0, 1]:
                   for dy in [-1, 0, 1]:
                       nx, ny = x + dx, y + dy
                       if 0 <= nx < size and 0 <= ny < size and board[ny][nx] != -1:
                           board[ny][nx] += 1
       
       return board

   def reveal_cell(self, board, visible_board, x, y, game):
       num_emojis = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣']
       
       queue = deque([(x, y)])
       visited = set()
       cells_revealed = 0
       
       while queue:
           cx, cy = queue.popleft()
           
           if not (0 <= cx < len(board[0]) and 0 <= cy < len(board)) or (cx, cy) in visited:
               continue
               
           if visible_board[cy][cx] != '⚪' and visible_board[cy][cx] != '<:minesweeperflag:1376450252860559430>':
               continue
           
           visited.add((cx, cy))
           
           if visible_board[cy][cx] == '<:minesweeperflag:1376450252860559430>':
               continue
           
           cell_value = board[cy][cx]
           visible_board[cy][cx] = num_emojis[cell_value] if 0 <= cell_value < len(num_emojis) else str(cell_value)
           cells_revealed += 1
           
           if cell_value == 0:
               for dx in [-1, 0, 1]:
                   for dy in [-1, 0, 1]:
                       queue.append((cx + dx, cy + dy))
       
       game['cells_uncovered'] += cells_revealed

   def check_win(self, board, visible_board, mines):
       hidden_cells = 0
       
       for y in range(len(board)):
           for x in range(len(board[0])):
               if visible_board[y][x] == '⚪' or visible_board[y][x] == '<:minesweeperflag:1376450252860559430>':
                   hidden_cells += 1
       
       return hidden_cells == mines

   def format_board_display(self, game):
       visible_board = game['visible_board']
       size = game['size']
       difficulty = game['difficulty']
       mines = game['mines']
       
       num_emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
       
       header = (
           f"⭐ **Dificultad:** {difficulty}\n"
           f"<:minesweeperflag:1376450252860559430> **Minas:** {mines}\n\n\n"
       )
       
       board_str = "⬛⬛"
       for i in range(size):
           board_str += num_emojis[i]
       board_str += "\n⬛⬛"
       board_str += "⬛" * size
       board_str += "\n"
       
       for y in range(size):
           board_str += num_emojis[y] + "⬛"
           for x in range(size):
               board_str += visible_board[y][x]
           board_str += "\n"
       
       if game.get('show_instructions', False):
           footer = (
               "\n-# Para jugar escribe `{coordenada-horizontal} {coordenada-vertical}`. "
               "Siendo `{coordenada-horizontal}` los números de arriba y `{coordenada-vertical}` los números en el lado. "
               "Para poner una bandera pon el mismo comando pero poniendo también `flag`\n"
               "-# Ejemplos: \n"
               "-# `3 2 flag` (se coloca una bandera en 3 2)\n"
               "-# `3 2` (se descubre la casilla 3 2)"
           )
           return header + board_str + footer
       else:
           return header + board_str
   
   def save_game_stats(self, user_id, game, result, points=0):
       try:
           if game.get('end_time') and game.get('start_time'):
               game_time = (game['end_time'] - game['start_time']).total_seconds()
           else:
               game_time = (datetime.now() - game.get('start_time', datetime.now())).total_seconds()
           
           game_data = {
               'difficulty': game.get('difficulty', 'Desconocida'),
               'result': result,
               'time': game_time,
               'cells_uncovered': game.get('cells_uncovered', 0),
               'flags_placed': game.get('flags_placed', 0),
               'correct_flags': game.get('correct_flags', 0),
               'points': points
           }
           
           update_minesweeper_stats(user_id, game_data)
       except Exception as e:
           print(f"Error al guardar estadísticas de buscaminas: {e}")

class GameManagementView(discord.ui.View):
   def __init__(self, cog, user_id):
       super().__init__(timeout=60)
       self.cog = cog
       self.user_id = user_id
   
   @discord.ui.button(label="Crear nueva partida", style=discord.ButtonStyle.primary)
   async def new_game(self, interaction: discord.Interaction, button: discord.ui.Button):
       if interaction.user.id != self.user_id:
           await interaction.response.send_message("Solo el dueño de la partida puede usar estos botones.", ephemeral=True)
           return
           
       if self.user_id in self.cog.active_games:
           game = self.cog.active_games[self.user_id]
           self.cog.save_game_stats(self.user_id, game, 'abandoned')
           del self.cog.active_games[self.user_id]
           
       if self.user_id in self.cog.last_interaction:
           del self.cog.last_interaction[self.user_id]
           
       if self.user_id in self.cog.game_messages:
           del self.cog.game_messages[self.user_id]
           
       await interaction.response.send_message("Partida anterior cancelada. Usa `/buscaminas` para crear una nueva.", ephemeral=True)
   
   @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.secondary)
   async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
       if interaction.user.id != self.user_id:
           await interaction.response.send_message("Solo el dueño de la partida puede usar estos botones.", ephemeral=True)
           return
           
       await interaction.response.send_message("Continúa tu partida actual.", ephemeral=True)

async def setup(bot):
   await bot.add_cog(Minesweeper(bot))