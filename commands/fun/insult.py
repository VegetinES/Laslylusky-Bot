import discord
from discord.ext import commands
from discord import app_commands
import random
import os
import google.generativeai as genai
from database.get import get_specific_field

class InsultCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        self.insultos = [
            "Eres tan feo que cuando naciste, el médico te abofeteó a tu madre.",
            "Tienes tanta suerte en el amor como un pez en el desierto.",
            "Tu sentido del humor es más seco que el papel de lija.",
            "Si las ideas fueran dinero, estarías en bancarrota.",
            "Eres tan aburrido que los juguetes no querían jugar contigo cuando eras pequeño.",
            "Pareces el tipo de persona que se emocionaría por recibir calcetines en Navidad.",
            "Tu cara asusta hasta a las calabazas de Halloween.",
            "Tu personalidad tiene tantas capas como una cebolla... igual de olorosa y hace llorar a la gente.",
            "Si fueras un condimento, serías harina.",
            "Tienes menos orientación que una brújula en el Triángulo de las Bermudas.",
            "Eres tan útil como un paraguas en el desierto.",
            "Tu cerebro tiene tantas arrugas como una pelota de ping-pong.",
            "Si la estupidez fuera música, serías una orquesta sinfónica.",
            "Tienes la gracia de un elefante en una tienda de porcelana.",
            "Eres la razón por la que los extraterrestres no nos visitan."
        ]
        
        self.prompts = [
            "Genera un insulto divertido y no ofensivo para {usuario} de 1 a 2 frases.",
            "Crea una burla amistosa y humorística para {usuario} de 1 a 2 frases.",
            "Escribe un insulto cómico e inofensivo dirigido a {usuario} de 1 a 2 frases.",
            "Elabora un insulto gracioso que no sea realmente hiriente para {usuario} de 1 a 2 frases."
        ]
        
        self.api_key = os.getenv("GEMINI")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    @commands.command(name="insulto")
    async def insulto_command(self, ctx, miembro: discord.Member = None):
        act_commands = get_specific_field(ctx.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if "insulto" not in act_commands:
            await ctx.reply("El comando no está activado en este servidor.")
            return
        
        await self.insulto_logic(ctx, miembro)

    @app_commands.command(name="insulto", description="Envía un insulto divertido a un usuario")
    @app_commands.describe(usuario="Usuario al que quieres insultar")
    async def insulto_slash(self, interaction: discord.Interaction, usuario: discord.Member = None):
        act_commands = get_specific_field(interaction.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
            return
        
        if "insulto" not in act_commands:
            await interaction.response.send_message("El comando no está activado en este servidor.")
            return
        
        await interaction.response.defer()
        await self.insulto_logic(interaction, usuario)

    async def insulto_logic(self, ctx, miembro=None):
        is_interaction = isinstance(ctx, discord.Interaction)
        author = ctx.user if is_interaction else ctx.author
        
        if isinstance(ctx.channel, discord.DMChannel):
            return
        
        act_commands = get_specific_field(ctx.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            return await ctx.followup.send(embed=embed) if is_interaction else await ctx.send(embed=embed)
        
        if "insulto" not in act_commands:
            mensaje = "El comando no está activado en este servidor."
            return await ctx.followup.send(mensaje) if is_interaction else await ctx.reply(mensaje)
        
        if miembro is None:
            miembro = author
        
        if miembro.id == self.bot.user.id:
            mensaje = "¡Oye! No puedo insultarme a mí mismo. Mejor insúltate tú. 😎"
            return await ctx.followup.send(mensaje) if is_interaction else await ctx.send(mensaje)
        
        try:
            prompt = random.choice(self.prompts)
            formatted_prompt = prompt.format(usuario=miembro.display_name)
            
            response = self.model.generate_content(formatted_prompt)
            insulto = response.text.strip()
            
            if not insulto or len(insulto) > 150 or "no puedo" in insulto.lower() or "contenido" in insulto.lower():
                insulto = random.choice(self.insultos)
        except Exception:
            insulto = random.choice(self.insultos)
        
        mensaje = f"🎯 {miembro.mention}, {insulto.lower()}"
        
        await ctx.followup.send(mensaje) if is_interaction else await ctx.send(mensaje)

async def setup(bot):
    await bot.add_cog(InsultCommand(bot))