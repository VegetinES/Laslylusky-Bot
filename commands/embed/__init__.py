from .embed import EmbedCommand

async def setup(bot):
    await bot.add_cog(EmbedCommand(bot))