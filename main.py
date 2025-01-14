import discord
from discord.ext import commands
# from dotenv import load_dotenv
import os
import glob
import webserver

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

#load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='%', intents=intents)

# Eliminar el comando 'help' predeterminado
bot.remove_command('help')

@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.idle,
        activity=discord.Game(name="En mantenimiento, se vienen cosas")
    )
    print(f"Estamos dentro! {bot.user}")

    for file in glob.glob("commands/*.py"):
        if file.endswith(".py"):
            extension = file[:-3].replace("\\", ".").replace("/", ".")
            try:
                await bot.load_extension(extension)
                print(f"Comando cargado: {extension}")
            except Exception as e:
                print(f"Error cargando {extension}: {e}")

# bot.run(os.getenv('DISCORD_TOKEN'))

webserver.keep_alive()
bot.run(DISCORD_TOKEN)