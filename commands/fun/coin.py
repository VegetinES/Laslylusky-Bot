import discord
from discord.ext import commands
from discord import app_commands
import random

from database.get import get_specific_field

class CoinCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="moneda")
    async def moneda_command(self, ctx):
        act_commands = get_specific_field(ctx.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if "moneda" not in act_commands:
            await ctx.reply("El comando no está activado en este servidor.")
            return

        await self.moneda_logic(ctx)

    @app_commands.command(name="moneda", description="Lanza una moneda: cara o cruz")
    async def moneda_slash(self, interaction: discord.Interaction):
        act_commands = get_specific_field(interaction.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
            return
        
        if "moneda" not in act_commands:
            await interaction.response.send_message("El comando no está activado en este servidor.")
            return
        
        await interaction.response.defer()
        await self.moneda_logic(interaction)

    async def moneda_logic(self, ctx):
        is_interaction = isinstance(ctx, discord.Interaction)
        user = ctx.user if is_interaction else ctx.author
        
        resultado = random.choice(["cara", "cruz"])
        
        emoji = "<a:coin:1372872655375437934>"
        
        embed = discord.Embed(
            title=f"{emoji} ¡Lanzamiento de moneda!",
            description=f"**Resultado: {resultado.upper()}**",
            color=discord.Color.gold()
        )
        
        embed.set_footer(text=f"Lanzada por {user.display_name}", icon_url=user.display_avatar.url)
        
        embed.set_thumbnail(url=f"https://i.imgur.com/{'aUEvNI5' if resultado == 'cara' else 'Syb31Xt'}.png")
        
        await ctx.followup.send(embed=embed) if is_interaction else await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(CoinCommand(bot))