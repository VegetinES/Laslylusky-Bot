from database.get import get_specific_field
import discord
from discord.ext import commands
import aiohttp
import base64
from io import BytesIO
import time

async def get_server_status(ip, platform):
    try:
        start_time = time.time()
        
        if platform == "bedrock":
            url = f"https://api.mcsrvstat.us/bedrock/3/{ip}"
        else:
            url = f"https://api.mcsrvstat.us/3/{ip}"
            
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    latency = int((time.time() - start_time) * 1000)
                    data['latency'] = latency
                    return data
                    
        return None
    except Exception as e:
        print(f"Error en get_server_status: {e}")
        return None

class McStatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="mcstatus")
    async def status(self, ctx, server: str = None, platform: str = None):
        if isinstance(ctx.channel, discord.DMChannel):
            return
        
        act_commands = get_specific_field(ctx.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if "mcstatus" not in act_commands:
            await ctx.reply("El comando no está activado en este servidor.")
            return
        
        try:
            if not server:
                await ctx.send("Por favor, proporciona la IP del servidor")
                return
                
            if not platform:
                await ctx.send("Por favor, especifica la plataforma ('java' o 'bedrock')")
                return
                
            platform = platform.lower()
            if platform not in ["java", "bedrock"]:
                await ctx.send("La plataforma debe ser 'java' o 'bedrock'")
                return

            print(f"Servidor: {server}, Plataforma: {platform}")
            status_message = await ctx.send("Obteniendo estado del servidor...")

            server_status = await get_server_status(server, platform)
            if not server_status:
                await status_message.edit(content=f"❌ No se pudo conectar al servidor {server}. Verifica que la IP sea correcta y el servidor esté en línea.")
                return
                
            print(f"Estructura de datos recibida: {server_status}")
            
            is_online = server_status.get("online", False)
            print(f"Estado online: {is_online}")
            
            if not is_online:
                await status_message.edit(content=f"⚠️ *¡El servidor {server} está fuera de línea!*")
                return

            players_online = server_status.get("players", {}).get("online", 0)
            max_players = server_status.get("players", {}).get("max", "?")

            motd_clean = server_status.get("motd", {}).get("clean", ["Sin MOTD"])
            motd = motd_clean[0] if isinstance(motd_clean, list) and motd_clean else "Sin MOTD"

            version = server_status.get("version", "No especificada")

            if "protocol" in server_status and "name" in server_status["protocol"]:
                protocol_version = server_status["protocol"]["name"]

                if protocol_version != version:
                    version = f"{version} (Protocolo: {protocol_version})"
                
            latency = f"{server_status.get('latency', '?')}ms"

            player_list = server_status.get("players", {}).get("list", [])
            
            embed = discord.Embed(
                title=f"Estado de {server} ({platform.capitalize()})", 
                color=discord.Color.green() if players_online > 0 else discord.Color.orange()
            )
            embed.add_field(name="📝 MOTD:", value=motd, inline=False)
            embed.add_field(name="🔧 Versión:", value=version, inline=True)
            embed.add_field(name="📶 Latencia:", value=latency, inline=True)
            embed.add_field(name="👥 Jugadores online:", value=f"{players_online}/{max_players}", inline=False)

            if "software" in server_status:
                embed.add_field(name="💻 Software:", value=server_status["software"], inline=True)

            if platform == "bedrock" and "gamemode" in server_status:
                embed.add_field(name="🎮 Modo de juego:", value=server_status["gamemode"], inline=True)

            if player_list:
                players_text = ", ".join([player.get("name", "Desconocido") for player in player_list])
                if len(players_text) > 1024:
                    players_text = players_text[:1021] + "..."
                embed.add_field(name="🎮 Jugadores:", value=players_text, inline=False)

            if "plugins" in server_status and server_status["plugins"]:
                plugins_text = ", ".join([f"{plugin.get('name', 'Desconocido')} ({plugin.get('version', 'v?')})" for plugin in server_status["plugins"]])
                if len(plugins_text) > 1024:
                    plugins_text = plugins_text[:1021] + "..."
                embed.add_field(name="🔌 Plugins:", value=plugins_text, inline=False)

            if "mods" in server_status and server_status["mods"]:
                mods_text = ", ".join([f"{mod.get('name', 'Desconocido')} ({mod.get('version', 'v?')})" for mod in server_status["mods"]])
                if len(mods_text) > 1024:
                    mods_text = mods_text[:1021] + "..."
                embed.add_field(name="📦 Mods:", value=mods_text, inline=False)
            
            try:
                if "icon" in server_status and server_status["icon"]:
                    icon_data = server_status["icon"].split(",")[1]
                    icon_bytes = base64.b64decode(icon_data)
                    file = discord.File(fp=BytesIO(icon_bytes), filename="server_icon.png")
                    embed.set_thumbnail(url="attachment://server_icon.png")
                    await status_message.delete()
                    await ctx.send(embed=embed, file=file)
                else:
                    await status_message.delete()
                    await ctx.send(embed=embed)
            except Exception as e:
                print(f"Error con el icono: {e}")
                await status_message.delete()
                await ctx.send(embed=embed)
                
        except Exception as e:
            print(f"Error en el comando mcstatus: {e}")
            await ctx.send(f"Ha ocurrido un error. Por favor, repórtelo con %bugreport [razón] y por favor específica el comando que dio error y pon esto también: {str(e)}")

async def setup(bot):
    await bot.add_cog(McStatus(bot))