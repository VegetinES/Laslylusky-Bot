import discord
from discord.ext import commands

class ServerIcon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="servericon")
    async def servericon(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
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