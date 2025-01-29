import discord
from discord.ext import commands
from singleton import database

class EmbedCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="embed")
    async def embed(self, ctx, *, mensaje: str = None):
        if isinstance(ctx.channel, discord.DMChannel):
            return
        
        if not mensaje:
            await ctx.send("Por favor, escribe un mensaje")
            return

        await ctx.message.delete()

        embed = discord.Embed(
            description=mensaje,
            color=discord.Color.random()
        )

        embed.set_footer(
            text=f"Enviado por: {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url
        )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(EmbedCommand(bot))