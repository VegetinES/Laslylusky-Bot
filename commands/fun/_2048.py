import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio

from database.get import get_specific_field

class Game2048:
    def __init__(self, user):
        self.user = user
        self.board = [[0 for _ in range(4)] for _ in range(4)]
        self.score = 0
        self.game_over = False
        self.won = False
        self.emojis = {
            0: "⬜",
            2: "<:2_:1375412380967895080>",
            4: "<:4_:1375412378392461383>",
            8: "<:8_:1375412375427219576>",
            16: "<:16:1375412370821746778>",
            32: "<:32:1375412366551810160>",
            64: "<:64:1375412362592649236>",
            128: "<:128:1375412359581007953>",
            256: "<:256:1375412356376694824>",
            512: "<:512:1375412352874319944>",
            1024: "<:1024:1375412348138950727>",
            2048: "<:2048:1375412344624123934>",
            4096: "<:4096:1375412340958429204>",
            8192: "<:8192:1375412329943928932>"
        }
        self.add_random_tile()
    
    def add_random_tile(self):
        empty_cells = []
        for i in range(4):
            for j in range(4):
                if self.board[i][j] == 0:
                    empty_cells.append((i, j))
        
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.board[i][j] = 2 if random.random() < 0.9 else 4
    
    def move_left(self):
        moved = False
        for i in range(4):
            row = [cell for cell in self.board[i] if cell != 0]
            
            for j in range(len(row) - 1):
                if row[j] == row[j + 1]:
                    row[j] *= 2
                    row[j + 1] = 0
                    self.score += row[j]
                    if row[j] == 8192:
                        self.won = True
            
            row = [cell for cell in row if cell != 0]
            row += [0] * (4 - len(row))
            
            if self.board[i] != row:
                moved = True
                self.board[i] = row
        
        return moved
    
    def move_right(self):
        for i in range(4):
            self.board[i] = self.board[i][::-1]
        moved = self.move_left()
        for i in range(4):
            self.board[i] = self.board[i][::-1]
        return moved
    
    def move_up(self):
        self.board = list(map(list, zip(*self.board)))
        moved = self.move_left()
        self.board = list(map(list, zip(*self.board)))
        return moved
    
    def move_down(self):
        self.board = list(map(list, zip(*self.board)))
        for i in range(4):
            self.board[i] = self.board[i][::-1]
        moved = self.move_left()
        for i in range(4):
            self.board[i] = self.board[i][::-1]
        self.board = list(map(list, zip(*self.board)))
        return moved
    
    def can_move(self):
        for i in range(4):
            for j in range(4):
                if self.board[i][j] == 0:
                    return True
                
                if j < 3 and self.board[i][j] == self.board[i][j + 1]:
                    return True
                
                if i < 3 and self.board[i][j] == self.board[i + 1][j]:
                    return True
        
        return False
    
    def get_board_string(self):
        board_str = ""
        for row in self.board:
            for cell in row:
                board_str += self.emojis[cell]
            board_str += "\n"
        return board_str.strip()
    
    def make_move(self, direction):
        if self.game_over:
            return False
        
        moved = False
        if direction == "up":
            moved = self.move_up()
        elif direction == "down":
            moved = self.move_down()
        elif direction == "left":
            moved = self.move_left()
        elif direction == "right":
            moved = self.move_right()
        
        if moved:
            self.add_random_tile()
            
            if not self.can_move():
                self.game_over = True
        
        return moved

class Game2048View(discord.ui.View):
    def __init__(self, game):
        super().__init__(timeout=300)
        self.game = game
    
    @discord.ui.button(emoji="<:blank:1375416823620833371>", style=discord.ButtonStyle.secondary, disabled=True, row=0)
    async def empty_button_1(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass
    
    @discord.ui.button(emoji="<:up:1375418108117782548>", style=discord.ButtonStyle.primary, row=0)
    async def move_up(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.game.user:
            await interaction.response.send_message("¡Este no es tu juego!", ephemeral=True)
            return
        
        if self.game.make_move("up"):
            await self.update_game(interaction)
        else:
            await interaction.response.defer()
    
    @discord.ui.button(emoji="<:blank:1375416823620833371>", style=discord.ButtonStyle.secondary, disabled=True, row=0)
    async def empty_button_2(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass
    
    @discord.ui.button(emoji="<:left:1375418114497581106>", style=discord.ButtonStyle.primary, row=1)
    async def move_left(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.game.user:
            await interaction.response.send_message("¡Este no es tu juego!", ephemeral=True)
            return
        
        if self.game.make_move("left"):
            await self.update_game(interaction)
        else:
            await interaction.response.defer()
    
    @discord.ui.button(emoji="<:down:1375418117223747676>", style=discord.ButtonStyle.primary, row=1)
    async def move_down(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.game.user:
            await interaction.response.send_message("¡Este no es tu juego!", ephemeral=True)
            return
        
        if self.game.make_move("down"):
            await self.update_game(interaction)
        else:
            await interaction.response.defer()
    
    @discord.ui.button(emoji="<:right:1375418110945001482>", style=discord.ButtonStyle.primary, row=1)
    async def move_right(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.game.user:
            await interaction.response.send_message("¡Este no es tu juego!", ephemeral=True)
            return
        
        if self.game.make_move("right"):
            await self.update_game(interaction)
        else:
            await interaction.response.defer()
    
    async def update_game(self, interaction):
        embed = discord.Embed(
            title=f"2048 de {self.game.user.name}",
            description=self.game.get_board_string(),
            color=0x237a4b
        )
        
        if self.game.score > 0:
            embed.add_field(name="Puntuación", value=str(self.game.score), inline=True)
        
        if self.game.won:
            embed.add_field(name="Estado", value="¡Has ganado! 🎉", inline=True)
            for item in self.children:
                item.disabled = True
        elif self.game.game_over:
            embed.add_field(name="Estado", value="Game Over 😢", inline=True)
            for item in self.children:
                item.disabled = True
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

class Game2048Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="2048", description="Juega al 2048")
    async def slash_2048(self, interaction: discord.Interaction):
        act_commands = get_specific_field(interaction.guild_id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if "2048" not in act_commands:
            await interaction.response.send_message("El comando no está activado en este servidor.", ephemeral=True)
            return
        
        game = Game2048(interaction.user)
        view = Game2048View(game)
        
        embed = discord.Embed(
            title=f"2048 de {interaction.user.name}",
            description=game.get_board_string(),
            color=0x237a4b
        )
        
        await interaction.response.send_message(embed=embed, view=view)
    
    @commands.command(name="2048")
    async def prefix_2048(self, ctx):
        act_commands = get_specific_field(ctx.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if "2048" not in act_commands:
            await ctx.reply("El comando no está activado en este servidor.")
            return

        game = Game2048(ctx.author)
        view = Game2048View(game)
        
        embed = discord.Embed(
            title=f"2048 de {ctx.author.name}",
            description=game.get_board_string(),
            color=0x237a4b
        )
        
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Game2048Commands(bot))