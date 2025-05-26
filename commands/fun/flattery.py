import discord
from discord.ext import commands
from discord import app_commands
import random
import os
import google.generativeai as genai
from database.get import get_specific_field

class FlatteryCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        self.halagos = [
            "Tu sonrisa ilumina hasta el día más oscuro.",
            "Tienes una forma única de hacer que todos se sientan especiales.",
            "Tu creatividad no conoce límites, es realmente inspiradora.",
            "La manera en que enfrentas los desafíos demuestra tu increíble fortaleza.",
            "Tu presencia hace que cualquier lugar sea mejor.",
            "Tienes una mente brillante que siempre ve soluciones donde otros ven problemas.",
            "Tu amabilidad hacia los demás es un regalo para el mundo.",
            "Tienes un sentido del humor que alegra a todos a tu alrededor.",
            "La pasión que pones en lo que haces es admirable y contagiosa.",
            "Eres como un diamante: valioso, único y resistente bajo presión.",
            "Si el mundo tuviera más personas como tú, sería un lugar mucho mejor.",
            "Tu honestidad y autenticidad son refrescantes en un mundo de apariencias.",
            "Tienes un talento natural para hacer que los demás se sientan valorados.",
            "Tu optimismo es como un faro de luz en medio de la tormenta.",
            "Tienes una belleza que va mucho más allá de lo físico y que ilumina desde dentro."
        ]
        
        self.prompts = [
            "Genera un halago bonito para {usuario} de 1 a 2 frases.",
            "Escribe un cumplido elegante y positivo para {usuario} de 1 a 2 frases.",
            "Crea un mensaje que resalte las cualidades de {usuario} de 1 a 2 frases.",
            "Elabora un halago creativo y sincero para {usuario} de 1 a 2 frases."
        ]
        
        self.api_key = os.getenv("GEMINI")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    @commands.command(name="halago")
    async def halago_command(self, ctx, miembro: discord.Member = None):
        act_commands = get_specific_field(ctx.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if "halago" not in act_commands:
            await ctx.reply("El comando no está activado en este servidor.")
            return
        
        await self.halago_logic(ctx, miembro)

    @app_commands.command(name="halago", description="Envía un halago bonito a un usuario")
    @app_commands.describe(usuario="Usuario al que quieres halagar")
    async def halago_slash(self, interaction: discord.Interaction, usuario: discord.Member = None):
        act_commands = get_specific_field(interaction.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
            return
        
        if "halago" not in act_commands:
            await interaction.response.send_message("El comando no está activado en este servidor.")
            return

        await interaction.response.defer()
        await self.halago_logic(interaction, usuario)

    async def halago_logic(self, ctx, miembro=None):
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
        
        if "halago" not in act_commands:
            mensaje = "El comando no está activado en este servidor."
            return await ctx.followup.send(mensaje) if is_interaction else await ctx.reply(mensaje)
        
        if miembro is None:
            miembro = author
        
        if miembro.id == self.bot.user.id:
            mensaje = "¡Gracias! Pero prefiero dar halagos que recibirlos. ¿A quién más podría halagar?"
            return await ctx.followup.send(mensaje) if is_interaction else await ctx.send(mensaje)
        
        try:
            prompt = random.choice(self.prompts)
            formatted_prompt = prompt.format(usuario=miembro.display_name)
            
            response = self.model.generate_content(formatted_prompt)
            halago = response.text.strip()
            
            if not halago or len(halago) > 150 or "no puedo" in halago.lower() or "contenido" in halago.lower():
                halago = random.choice(self.halagos)
        except Exception:
            halago = random.choice(self.halagos)
        
        mensaje = f"✨ {miembro.mention}, {halago.lower()}"
        
        await ctx.followup.send(mensaje) if is_interaction else await ctx.send(mensaje)

async def setup(bot):
    await bot.add_cog(FlatteryCommand(bot))