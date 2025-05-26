import discord
from discord import app_commands
from discord.ext import commands
import json
import random
import asyncio
from pymongo import MongoClient
from datetime import datetime
import os

from database.get import get_specific_field

class TriviaView(discord.ui.View):
    def __init__(self, author_id, pregunta, correcta, timeout=60):
        super().__init__(timeout=timeout)
        self.author_id = author_id
        self.correcta = correcta
        self.pregunta = pregunta
        self.answered = False
    
    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        
        embed = discord.Embed(
            title="¡Tiempo agotado!",
            description=f"**Pregunta:** {self.pregunta['pregunta']}\n\n"
                       f"**A:** {self.pregunta['a']}\n"
                       f"**B:** {self.pregunta['b']}\n"
                       f"**C:** {self.pregunta['c']}\n"
                       f"**D:** {self.pregunta['d']}\n\n"
                       f"La respuesta correcta era: **{self.correcta.upper()}** - {self.pregunta[self.correcta]}",
            color=discord.Color.orange()
        )
        
        try:
            await self.message.edit(embed=embed, view=self)
        except:
            pass
    
    @discord.ui.button(label="A", style=discord.ButtonStyle.primary)
    async def button_a(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_answer(interaction, "a")
    
    @discord.ui.button(label="B", style=discord.ButtonStyle.primary)
    async def button_b(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_answer(interaction, "b")
    
    @discord.ui.button(label="C", style=discord.ButtonStyle.primary)
    async def button_c(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_answer(interaction, "c")
    
    @discord.ui.button(label="D", style=discord.ButtonStyle.primary)
    async def button_d(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_answer(interaction, "d")
    
    async def process_answer(self, interaction: discord.Interaction, selected_option):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("No puedes responder a una trivia que no has iniciado.", ephemeral=True)
            return
        
        if self.answered:
            await interaction.response.send_message("Ya has respondido a esta pregunta.", ephemeral=True)
            return
        
        self.answered = True
        
        for item in self.children:
            item.disabled = True
        
        is_correct = selected_option == self.correcta
        
        client = MongoClient('mongodb://localhost:27017/')
        db = client['trivia_db']
        scores_collection = db['user_scores']
        
        user_data = scores_collection.find_one({"user_id": interaction.user.id})
        current_points = user_data["points"] if user_data else 0
        
        if is_correct:
            new_points = current_points + 1
            color = discord.Color.green()
            result_text = "¡Respuesta correcta! 🎉"
        else:
            new_points = max(0, current_points - 1)
            color = discord.Color.red()
            result_text = "Respuesta incorrecta 😔"
        
        scores_collection.update_one(
            {"user_id": interaction.user.id},
            {"$set": {"user_id": interaction.user.id, "points": new_points, "last_updated": datetime.now()}},
            upsert=True
        )
        
        embed = discord.Embed(
            title=result_text,
            description=f"**Pregunta:** {self.pregunta['pregunta']}\n\n"
                       f"**A:** {self.pregunta['a']}\n"
                       f"**B:** {self.pregunta['b']}\n"
                       f"**C:** {self.pregunta['c']}\n"
                       f"**D:** {self.pregunta['d']}\n\n"
                       f"La respuesta correcta era: **{self.correcta.upper()}** - {self.pregunta[self.correcta]}\n\n"
                       f"{interaction.user.mention} ahora tienes **{new_points}** puntos.",
            color=color
        )
        
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()

class Trivia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.trivia_data = None
        self.load_trivia_data()
    
    def load_trivia_data(self):
        try:
            possible_paths = [
                'trivia.json',
                os.path.join(os.path.dirname(__file__), 'trivia.json'),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trivia.json'),
                os.path.join(os.getcwd(), 'trivia.json')
            ]
            
            file_loaded = False
            for path in possible_paths:
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as file:
                        self.trivia_data = json.load(file)
                        print(f"Archivo trivia.json cargado correctamente desde: {path}")
                        file_loaded = True
                        break
            
            if not file_loaded:
                print(f"No se pudo encontrar el archivo trivia.json. Rutas intentadas: {possible_paths}")
                self.trivia_data = {"preguntas": []}
                
        except Exception as e:
            print(f"Error al cargar trivia.json: {str(e)}")
            self.trivia_data = {"preguntas": []}
    
    async def send_trivia(self, ctx, is_slash=False):
        if not self.trivia_data or not self.trivia_data.get("preguntas"):
            error_msg = "No se pudieron cargar las preguntas de trivia."
            if is_slash:
                await ctx.response.send_message(error_msg, ephemeral=True)
            else:
                await ctx.reply(error_msg)
            return
        
        pregunta = random.choice(self.trivia_data["preguntas"])
        
        embed = discord.Embed(
            title="¡Trivia!",
            description=f"**Pregunta:** {pregunta['pregunta']}\n\n"
                       f"**A:** {pregunta['a']}\n"
                       f"**B:** {pregunta['b']}\n"
                       f"**C:** {pregunta['c']}\n"
                       f"**D:** {pregunta['d']}",
            color=discord.Color.blue()
        )
        
        embed.set_footer(text="Tienes 60 segundos para responder")
        
        user_id = ctx.user.id if is_slash else ctx.author.id
        
        view = TriviaView(user_id, pregunta, pregunta['correcta'])
        
        if is_slash:
            await ctx.response.send_message(embed=embed, view=view)
            view.message = await ctx.original_response()
        else:
            view.message = await ctx.reply(embed=embed, view=view)
    
    @commands.command(name="trivia")
    async def trivia_command(self, ctx):
        act_commands = get_specific_field(ctx.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if "trivia" not in act_commands:
            await ctx.reply("El comando no está activado en este servidor.")
            return
    
        await self.send_trivia(ctx)
    
    @app_commands.command(name="trivia", description="Inicia un juego de trivia con preguntas aleatorias")
    async def trivia_slash(self, interaction: discord.Interaction):
        act_commands = get_specific_field(interaction.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
            return
        
        if "trivia" not in act_commands:
            await interaction.response.send_message("El comando no está activado en este servidor.")
            return
        
        await self.send_trivia(interaction, is_slash=True)

async def setup(bot):
    await bot.add_cog(Trivia(bot))