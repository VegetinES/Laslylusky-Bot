import discord
from discord.ext import commands
import os
import glob
import asyncio
import webserver
from database import Database

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='%', intents=intents)

bot.remove_command('help')

def DB():
    database = Database()
    database.connection()
    db = database.get_collection()

    return db

db = DB()

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

# CAMBIAR QUE SI SE UNE SIN ADMIN SE INSERTEN UNOS DATOS, Y SINO SE INSERTAN CON OTROS DATOS
# Y HACER LO MISMO EN update-data.py
# Y AÑADIR UN COMANDO QUE SE RESTABLEZCA LA CONFIGURACIÓN, Y QUE PERMITE CONFIGURAR NUEVAMENTE LOS DATOS SI SE AÑADEN PERMISOS DE ADMINISTRADOR MÁS TARDE

"""
@bot.event
async def on_guild_join(guild):   
    data = {
        "guild_id": guild.id,
        "guild_name": guild.name,
        "member_count": guild.member_count,
        "act_cmd": ["help", "invite", "info", "updates", "ping", "serverinfo"],
        "deact_cmd": ["hi", "embed"],
        "perms": {
            "mg-ch-roles": [role.id for role in guild.roles if role.permissions.manage_channels],
            "mg-ch-users": [member.id for member in guild.members if member.guild_permissions.manage_channels],
            "admin-roles": [role.id for role in guild.roles if role.permissions.administrator],
            "admin-users": [member.id for member in guild.members if member.guild_permissions.administrator]
        },
        "audit_logs": {
            "ban": {
                "log_channel": "",
                "ban_messages": "",
                "activated": True
            },
            "kick": {
                "log_channel": "",
                "kick_messages": "",
                "activated": False
            }
        },
        "cmd": {
            "hi": "",
            "stats": "",
            "ping": "",
            "mute": ""
        }
    }
    
    db.insert_one(data)
    
    print(f"Se ha unido al servidor: {guild.name} (ID: {guild.id})")
"""

"""
@bot.event
async def on_guild_remove(guild):
    guild_id = guild.id
    
    # Eliminar el documento de la colección donde el guild_id coincide
    result = db.delete_one({"guild_id": guild_id})
    
    if result.deleted_count > 0:
        print(f"Se han eliminado los datos del servidor: {guild.name} (ID: {guild_id})")
    else:
        print(f"No se encontraron datos para el servidor: {guild.name} (ID: {guild_id})")
"""

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