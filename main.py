import discord
from discord.ext import commands, tasks
import os
import glob
import asyncio
from commands.utility.birthday.database import BirthdayDB
import webserver
from database.save import save_server_data
from database.delete import delete_server_data
from database.connection import mongo_db
from database.iadatabase import database
import sys
from database.oracle import Oracle
import datetime
from commands.tickets.listeners import TicketDatabaseListener
import signal

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix='%', intents=intents)

ticket_listener = None
shutdown_event = asyncio.Event()

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
                from commands.tickets.utils.helpers import get_ticket_data
                
                ticket_config = get_ticket_data(message.guild.id, str(parent_channel.id))
                if ticket_config:
                    from commands.tickets.utils.helpers import reopen_ticket
                    await reopen_ticket(thread, message.author)

@bot.event
async def on_thread_create(thread):
    try:
        await thread.join()
        print(f"Bot se unió al nuevo hilo: {thread.name} en {thread.guild.name}")
    except discord.Forbidden:
        print(f"No se pudo unir al nuevo hilo: {thread.name} (sin permisos)")
    except discord.HTTPException as e:
        print(f"Error al unirse al nuevo hilo {thread.name}: {e}")
    except Exception as e:
        print(f"Error inesperado al unirse al nuevo hilo {thread.name}: {e}")

@bot.event
async def on_thread_update(before, after):
    if before.me is None and after.me is None:
        try:
            await after.join()
            print(f"Bot obtuvo acceso y se unió al hilo: {after.name} en {after.guild.name}")
        except discord.Forbidden:
            pass
        except discord.HTTPException:
            pass
        except Exception:
            pass

async def join_active_threads():
    for guild in bot.guilds:
        try:
            for channel in guild.channels:
                if isinstance(channel, (discord.TextChannel, discord.ForumChannel)):
                    for thread in channel.threads:
                        if thread.me is None and not thread.archived:
                            try:
                                await thread.join()
                                print(f"Bot se unió al hilo activo: {thread.name}")
                            except:
                                pass
        except Exception as e:
            print(f"Error revisando hilos activos en {guild.name}: {e}")

bot.remove_command('help')

oracle = Oracle()

@bot.event
async def on_ready():
    global ticket_listener
    
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(type=discord.ActivityType.listening, name="/help | %help")
    )
    print(f"Estamos dentro! {bot.user}")
    
    webserver.set_bot_instance(bot)
    
    await load_extensions(["commands", "logs"])

    try:
        await bot.tree.sync()
        print("Slash commands sincronizados correctamente")
    except Exception as e:
        print(f"Error sincronizando slash commands: {e}")

    print("Revisando hilos activos existentes...")
    await join_active_threads()
    print("Revisión de hilos activos completada")

    print("Iniciando listener de tickets...")
    ticket_listener = TicketDatabaseListener(bot)
    bot.ticket_listener = ticket_listener
    ticket_listener.start_listening()
    print("Listener de tickets iniciado")

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
    
    excluded_files = {
        'commands/voice/events.py',
        'commands/voice/config.py',
        'commands\\voice\\events.py',
        'commands\\voice\\config.py'
    }
    
    for directory in directories:
        main_files = [f for f in glob.glob(f"{directory}/*.py") 
                     if "__pycache__" not in f]
        
        subdir_files = [f for f in glob.glob(f"{directory}/**/*.py", recursive=True) 
                       if "__pycache__" not in f]
        
        subdir_files = [f for f in subdir_files if f not in main_files]
        
        all_files = main_files + subdir_files
        
        for file in all_files:
            if file.endswith(".py") and file not in excluded_files:
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
    global ticket_listener

    from data import get_data 

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

    if ticket_listener:
        ticket_listener.add_guild_listener(guild.id)

    print(f"Revisando hilos activos en el nuevo servidor: {guild.name}")
    try:
        for channel in guild.channels:
            if isinstance(channel, (discord.TextChannel, discord.ForumChannel)):
                for thread in channel.threads:
                    if thread.me is None and not thread.archived:
                        try:
                            await thread.join()
                            print(f"Bot se unió al hilo activo: {thread.name}")
                        except:
                            pass
    except Exception as e:
        print(f"Error revisando hilos activos en nuevo servidor {guild.name}: {e}")
        
@bot.event
async def on_guild_remove(guild):
    global ticket_listener
    
    try:
        birthday_db = BirthdayDB()
        
        await birthday_db.delete_config(guild.id)
        
        await birthday_db.delete_all_guild_birthdays(guild.id)
        
        print(f"Se han eliminado los datos de cumpleaños del servidor: {guild.name} (ID: {guild.id})")
    except Exception as e:
        print(f"Error al eliminar datos de cumpleaños: {e}")
    
    if ticket_listener:
        ticket_listener.remove_guild_listener(guild.id)
    
    success = delete_server_data(guild.id)

    if success:
        print(f"Se han eliminado los datos del servidor: {guild.name} (ID: {guild.id})")
    else:
        print(f"Error al eliminar datos del servidor: {guild.name} (ID: {guild.id})")

def signal_handler(signum, frame):
    print("\nSeñal de interrupción recibida, cerrando...")
    shutdown_event.set()

async def shutdown():
    global ticket_listener
    
    print("Iniciando proceso de cierre...")
    
    if ticket_listener:
        print("Deteniendo listener de tickets...")
        ticket_listener.stop_listening()
    
    print("Cerrando bot de Discord...")
    if not bot.is_closed():
        await bot.close()
    
    print("Cerrando conexiones...")
    try:
        oracle.close()
    except:
        pass

async def main():
    global ticket_listener
    
    try:
        print("Iniciando proceso principal...")
        print(f"Python version: {sys.version}")
        print(f"Discord.py version: {discord.__version__}")
        
        print("Conectando a MongoDB...")
        mongo_db.get_collection()
        print("MongoDB conectado")

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
        
        bot_task = asyncio.create_task(bot.start(DISCORD_TOKEN))
        shutdown_task = asyncio.create_task(shutdown_event.wait())
        
        done, pending = await asyncio.wait(
            [bot_task, shutdown_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        for task in pending:
            task.cancel()
        
        await shutdown()
        
    except discord.LoginFailure as e:
        print(f"Error de login: {e}")
    except Exception as e:
        print(f"Error inesperado: {type(e).__name__}: {e}")

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("Iniciando servidor web...")
    web_thread = webserver.keep_alive()
    print("Servidor web iniciado en segundo plano")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Cerrando por interrupción del usuario...")
    except Exception as e:
        print(f"Error crítico: {type(e).__name__}: {e}")
    finally:
        print("Proceso terminado")
    