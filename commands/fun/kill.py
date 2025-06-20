from database.get import get_specific_field
import discord
from discord.ext import commands
import random
import os 
import google.generativeai as genai

class Kill(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.prompts = [
            "Genera una muerte graciosa para {victim} causada por {killer} de 2 a 4 frases",
            "Describe cómo {killer} elimina a {victim} de forma cómica de 2 a 4 frases",
            "Escribe una pequeña historia divertida sobre cómo {killer} derrota a {victim} de 2 a 4 frases",
            "Narra un encuentro hilarante donde {killer} vence a {victim} de 2 a 4 frases"
        ]
        
        self.api_key = os.getenv("GEMINI")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")
        
    @commands.command()
    async def kill(self, ctx, victim: discord.Member = None):
        if isinstance(ctx.channel, discord.DMChannel):
            return
        
        act_commands = get_specific_field(ctx.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if "kill" not in act_commands:
            await ctx.reply("El comando no está activado en este servidor.")
            return

        if victim is None:
            await ctx.send("¡Necesitas mencionar a alguien!")
            return
            
        killer = ctx.author
        
        if victim == killer:
            await ctx.send("¡No puedes matarte a ti mismo!")
            return
            
        prompt = random.choice(self.prompts)
        
        formatted_prompt = prompt.format(
            victim=victim.display_name,
            killer=killer.display_name
        )
        
        try:
            response = self.model.generate_content(formatted_prompt)

            await ctx.send(response.text)
            
        except Exception as e:
            await ctx.send("¡Ups! Algo salió mal al generar la respuesta. ¡Inténtalo de nuevo!")
            print(f"Error: {e}")

async def setup(bot):
    await bot.add_cog(Kill(bot))