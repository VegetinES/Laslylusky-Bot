import discord
from discord.ext import commands, tasks
import os
import glob
import asyncio
import webserver
from database.save import save_server_data
from database.delete import delete_server_data
from database.connection import firebase_db
from database.iadatabase import database
import sys
from database.oracle import Oracle
import datetime

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix='%', intents=intents)

@bot.event
async def on_interaction(interaction):
    if interaction.type == discord.InteractionType.component:
        custom_id = interaction.data.get("custom_id", "")
        if custom_id.startswith("ticket:"):
            from commands.tickets.utils.helpers import handle_ticket_button
            await handle_ticket_button(interaction, custom_id)

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    
    if isinstance(message.channel, discord.Thread) and not message.author.bot:
        thread = message.channel
        
        if thread.archived:
            parent_channel = thread.parent
            if parent_channel:
                from commands.tickets.utils.database import get_ticket_data
                
                ticket_config = get_ticket_data(message.guild.id, str(parent_channel.id))
                if ticket_config:
                    from commands.tickets.utils.helpers import reopen_ticket
                    await reopen_ticket(thread, message.author)

bot.remove_command('help')

oracle = Oracle()

@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.idle,
        activity=discord.Game(name="En mantenimiento, se vienen cosas")
    )
    print(f"Estamos dentro! {bot.user}")
    
    await load_extensions(["commands", "logs"])

    try:
        await bot.tree.sync()
        print("Slash commands sincronizados correctamente")
    except Exception as e:
        print(f"Error sincronizando slash commands: {e}")

    update_oracle_db.start()

@tasks.loop(hours=24.0)
async def update_oracle_db():
    try:
        oracle.connect()
        try:
            result = oracle.update_temp(1)
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{current_time}] Base de datos Oracle actualizada exitosamente")
        finally:
            oracle.close()
    except Exception as e:
        print(f"Error al actualizar la base de datos Oracle: {e}")

@update_oracle_db.before_loop
async def before_update_oracle_db():
    await bot.wait_until_ready()

async def load_extensions(directories):
    total_extensions = 0
    main_extensions = 0
    subdir_extensions = 0
    
    for directory in directories:
        main_files = [f for f in glob.glob(f"{directory}/*.py") 
                     if "__pycache__" not in f]
        
        subdir_files = [f for f in glob.glob(f"{directory}/**/*.py", recursive=True) 
                       if "__pycache__" not in f]
        
        subdir_files = [f for f in subdir_files if f not in main_files]
        
        all_files = main_files + subdir_files
        
        for file in all_files:
            if file.endswith(".py"):
                extension = file[:-3].replace("\\", ".").replace("/", ".")
                
                try:
                    await bot.load_extension(extension)
                    print(f"Extensión cargada: {extension}")
                    total_extensions += 1
                    if file in main_files:
                        main_extensions += 1
                    else:
                        subdir_extensions += 1
                except Exception as e:
                    print(f"Error cargando {extension}: {e}")
    
    print(f"\nTotal de extensiones cargadas: {total_extensions}")
    print(f"Extensiones en directorios principales: {main_extensions}")
    print(f"Extensiones en subdirectorios: {subdir_extensions}")

@bot.event
async def on_guild_join(guild):  

    from .data import get_data 

    data = get_data(guild.id)
    
    success = save_server_data(guild, data)
    
    if success:
        print(f"Se ha unido y guardado datos del servidor: {guild.name} (ID: {guild.id})")
    else:
        print(f"Error al guardar datos del servidor: {guild.name} (ID: {guild.id})")

    try:
        oracle.connect()
        try:
            result = oracle.initialize_guild(str(guild.id))
            if "success" in result:
                print(f"Servidor {guild.id} inicializado en Oracle DB exitosamente")
            elif "warning" in result:
                print(f"Aviso: {result['warning']}")
            else:
                print(f"Error al inicializar servidor en Oracle DB: {result}")
        finally:
            oracle.close()
    except Exception as e:
        print(f"Error al inicializar servidor en Oracle DB: {e}")
        
@bot.event
async def on_guild_remove(guild):
    success = delete_server_data(guild.id)

    if success:
        print(f"Se han eliminado los datos del servidor: {guild.name} (ID: {guild.id})")
    else:
        print(f"Error al eliminar datos del servidor: {guild.name} (ID: {guild.id})")

async def main():
    try:
        print("Iniciando proceso principal...")
        print(f"Python version: {sys.version}")
        print(f"Discord.py version: {discord.__version__}")
        
        print("Conectando a Firebase...")
        firebase_db.get_reference()
        print("Firebase conectado")

        try:
            oracle.connect()
            print("Conectado a la base de datos oracle")

            result = oracle.update_temp(1)
            print("Base de datos Oracle actualizada al iniciar")
        except Exception as e:
            print(f"Error al conectar con la base de datos Oracle: {e}")
        finally:
            oracle.close()

        print("Iniciando bot de Discord...")
        try:
            await bot.start(DISCORD_TOKEN)
        except discord.LoginFailure as e:
            print(f"Error de login: {e}")
        except Exception as e:
            print(f"Error inesperado: {type(e).__name__}: {e}")
    except Exception as e:
        print(f"Error en main: {type(e).__name__}: {e}")

if __name__ == "__main__":
    print("Iniciando servidor web...")
    web_thread = webserver.keep_alive()
    print("Servidor web iniciado en segundo plano")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("Cerrando por interrupción del usuario...")
    except Exception as e:
        print(f"Error crítico: {type(e).__name__}: {e}")
    finally:
        loop.close()
