from .commands import ReminderCommands
from .scheduler import start_scheduler
import asyncio

async def setup(bot):
    if not bot.get_cog("ReminderCommands"):
        await bot.add_cog(ReminderCommands(bot))
        print("✅ Cog ReminderCommands cargado correctamente")
    else:
        print("⚠️ Cog ReminderCommands ya estaba cargado")
    
    bot.loop.create_task(start_scheduler(bot))
    print("✅ Sistema de recordatorios iniciado correctamente")