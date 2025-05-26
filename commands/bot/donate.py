import discord
from discord.ext import commands

class Donate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="donate")
    async def donate(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            return

        embed = discord.Embed(
            title="Donaciones",
            description=(f"Hola {ctx.author.mention}, aquí tienes el enlace para hacer donaciones para el bot, "
                         f"para que pueda seguir adelante: \n\n[PayPal](https://paypal.me/VegetinES)"),
            color=discord.Color.blue()
        )
        embed.set_thumbnail(
            url="https://i.imgur.com/if0NO2o.png"
        )
        embed.set_footer(text=f"Pedido por: {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)

        try:
            await ctx.author.send(embed=embed)
            await ctx.send(f"{ctx.author.mention}, ahí te mandé el enlace para donar por MD :).")
        except discord.Forbidden:
            await ctx.send(f"{ctx.author.mention}, no pude enviarte un mensaje directo. Aquí tienes la información sobre las donaciones:",
                           embed=embed)

async def setup(bot):
    await bot.add_cog(Donate(bot))