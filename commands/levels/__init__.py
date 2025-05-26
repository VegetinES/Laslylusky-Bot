from .level_commands import LevelCommands

async def setup(bot):
    await bot.add_cog(LevelCommands(bot))