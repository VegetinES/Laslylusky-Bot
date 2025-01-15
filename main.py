import discord
from discord.ext import commands
import os
import glob
import asyncio
import webserver

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='%', intents=intents)

bot.remove_command('help')

@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.idle,
        activity=discord.Game(name="En mantenimiento, se vienen cosas")
    )
    print(f"Estamos dentro! {bot.user}")
    
    await load_commands("commands")

async def load_commands(commands_dir):
    main_commands = [f for f in glob.glob(f"{commands_dir}/*.py") 
                    if "__pycache__" not in f]
    
    subdir_commands = [f for f in glob.glob(f"{commands_dir}/**/*.py", recursive=True) 
                      if "__pycache__" not in f]
    
    subdir_commands = [cmd for cmd in subdir_commands if cmd not in main_commands]
    
    all_commands = main_commands + subdir_commands
    
    for file in all_commands:
        if file.endswith(".py"):
            extension = file[:-3].replace("\\", ".").replace("/", ".")
            
            try:
                await bot.load_extension(extension)
                print(f"Comando cargado: {extension}")
            except Exception as e:
                print(f"Error cargando {extension}: {e}")
                
    print(f"\nTotal de comandos cargados: {len(all_commands)}")
    print(f"Comandos en directorio principal: {len(main_commands)}")
    print(f"Comandos en subdirectorios: {len(subdir_commands)}")

async def main():
    webserver.keep_alive()
    try:
        async with bot:
            await bot.start(DISCORD_TOKEN)
    except KeyboardInterrupt:
        print("\nApagando el bot...")
        await bot.close()
    finally:
        print("Bot apagado correctamente. Adiós!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSe recibió una señal de interrupción. Cerrando...")