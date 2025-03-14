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
    data = {
        "guild_id": guild.id,
        "default_cdm": ["help", "donate", "info", "invite", "privacidad", "updates", "savedatachat", "bot-suggest", "bugreport", "laslylusky", "reset-chat", "config", "infracciones", "moderador"],
        "act_cmd": ["serverinfo", "slowmode", "kill", "meme", "avatar", "servericon", "userinfo", "ban", "unban", "clear", "kick", "warn", "unwarn", "4k", "anal", "ass", "blowjob", "boobs", "hanal", "hass", "hboobs", "pgif", "pussy", "mcstatus", "mcuser", "hypixel", "hug", "massban", "purgeban"],
        "deact_cmd": ["embed"],
        "mute_role": 0,
        "perms": {
            "mg-ch-roles": [0],
            "mg-ch-users": [0],
            "admin-roles": [0],
            "admin-users": [0],
            "mg-rl-roles": [0],
            "mg-rl-user": [0],
            "mg-srv-roles": [0],
            "mg-srv-users": [0],
            "kick-roles": [0],
            "kick-users": [0],
            "ban-roles": [0],
            "ban-users": [0],
            "mute-roles": [0],
            "mute-users": [0],
            "deafen-roles": [0],
            "deafen-users": [0],
            "mg-msg-roles": [0],
            "mg-msg-users": [0],
            "warn-users": [0],
            "warn-roles": [0],
            "unwarn-users": [0],
            "unwarn-roles": [0]
        },
        "audit_logs": {
            "ban": {
                "log_channel": 0,
                "ban_messages": "None",
                "activated": False
            },
            "kick": {
                "log_channel": 0,
                "kick_messages": "None",
                "activated": False
            },
            "unban": {
                "log_channel": 0,
                "unban_messages": "None",
                "activated": False
            },
            "enter": {
                "log_channel": 0,
                "enter_messages": "None",
                "activated": False
            },
            "leave": {
                "log_channel": 0,
                "leave_messages": "None",
                "activated": False
            },
            "del_msg": { 
                "log_channel": 0, 
                "del_msg_messages": "None", 
                "ago": 7,
                "activated": False 
            }, 
            "edited_msg": { 
                "log_channel": 0, 
                "edited_msg_messages": "None", 
                "ago": 7,
                "activated": False 
            },
            "warn": {
                "log_channel": 0,
                "warn_messages": "None",
                "activated": False
            },
            "unwarn": {
                "log_channel": 0,
                "unwarn_messages": "None",
                "activated": False
            }
        },
        "tickets": {}
    } 
    
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
