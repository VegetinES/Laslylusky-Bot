from database.get import get_specific_field
import discord
from discord.ext import commands

class ServerIcon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="servericon")
    async def servericon(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            return
        
        act_commands = get_specific_field(ctx.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando </config update:1348248454610161751> si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if "servericon" not in act_commands:
            await ctx.reply("El comando no está activado en este servidor.")
            return

        icon_url = ctx.guild.icon.url if ctx.guild.icon else None

        if not icon_url:
            await ctx.reply("Este servidor no tiene un icono establecido.")
            return

        embed = discord.Embed(color=discord.Color.random())
        embed.set_image(url=icon_url)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ServerIcon(bot))