from .events import setup as setup_events
from .config import setup as setup_config

async def setup(bot):
    if "VoiceConfig" in bot.cogs and "VoiceEvents" in bot.cogs:
        print("Los cogs VoiceConfig y VoiceEvents ya están cargados")
        return
    
    try:
        if "VoiceConfig" in bot.cogs:
            await bot.remove_cog("VoiceConfig")
        if "VoiceEvents" in bot.cogs:
            await bot.remove_cog("VoiceEvents")
    except Exception as e:
        print(f"Error al eliminar cogs: {e}")
    
    try:
        await setup_config(bot)
        print("Cog VoiceConfig cargado correctamente")
    except Exception as e:
        print(f"Error al cargar config: {e}")
        
    try:
        await setup_events(bot)
        print("Cog VoiceEvents cargado correctamente")
    except Exception as e:
        print(f"Error al cargar events: {e}")