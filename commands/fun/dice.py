import discord
from discord.ext import commands
from discord import app_commands
import random

from database.get import get_specific_field

class DiceCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="dado")
    async def dado_command(self, ctx, caras: int = 6):
        act_commands = get_specific_field(ctx.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if "dado" not in act_commands:
            await ctx.reply("El comando no está activado en este servidor.")
            return
        
        await self.dado_logic(ctx, caras)

    @app_commands.command(name="dado", description="Tira un dado con el número de caras especificado")
    @app_commands.describe(caras="Número de caras del dado (predeterminado: 6)")
    async def dado_slash(self, interaction: discord.Interaction, caras: int = 6):
        act_commands = get_specific_field(interaction.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
            return
        
        if "dado" not in act_commands:
            await interaction.response.send_message("El comando no está activado en este servidor.")
            return

        await interaction.response.defer()
        await self.dado_logic(interaction, caras)

    async def dado_logic(self, ctx, caras=6):
        is_interaction = isinstance(ctx, discord.Interaction)
        user = ctx.user if is_interaction else ctx.author
        
        if caras < 2:
            mensaje = "Un dado debe tener al menos 2 caras."
            return await ctx.followup.send(mensaje) if is_interaction else await ctx.send(mensaje)
        
        if caras > 1000:
            mensaje = "El dado no puede tener más de 1000 caras."
            return await ctx.followup.send(mensaje) if is_interaction else await ctx.send(mensaje)
        
        resultado = random.randint(1, caras)
        
        embed = discord.Embed(
            title=f"🎲 Dado de {caras} caras",
            description=f"**Resultado: {resultado}**",
            color=discord.Color.blue()
        )
        
        embed.set_footer(text=f"Tirado por {user.display_name}", icon_url=user.display_avatar.url)
        
        if caras == 20:
            if resultado == 20:
                embed.add_field(name="¡CRÍTICO!", value="¡Has sacado el máximo posible!", inline=False)
                embed.color = discord.Color.green()
            elif resultado == 1:
                embed.add_field(name="¡PIFIA!", value="¡Has sacado el mínimo posible!", inline=False)
                embed.color = discord.Color.red()
        
        await ctx.followup.send(embed=embed) if is_interaction else await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(DiceCommand(bot))