from .commands import Birthday
from .task import BirthdayTask

async def setup(bot):
    await bot.add_cog(Birthday(bot))
    await bot.add_cog(BirthdayTask(bot))
    print("📅 Sistema de cumpleaños cargado")