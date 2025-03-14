from database.get import get_specific_field
import discord
from discord.ext import commands
import aiohttp
import os
import asyncio

class Hypixel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.player_profile_cache = {}
        self.CACHE_DURATION = 120

    def format_number(self, number):
        return "{:,}".format(int(number))

    def format_timestamp(self, timestamp):
        if not timestamp or timestamp == "Desconocido":
            return "Desconocido"
        try:
            ts = int(int(timestamp)/1000)
            return f"<t:{ts}:f>"
        except:
            return "Fecha inválida"

    def create_stats_string(self, stats, include_souls=False):
        parts = []
        if include_souls and 'almas' in stats:
            parts.append(f"👻 Almas: `{self.format_number(stats['souls'])}`")
        if 'monedas' in stats:
            parts.append(f"💰 Monedas: `{self.format_number(stats['coins'])}`")
        if 'asesinatos' in stats:
            parts.append(f"⚔️ Asesinatos: `{self.format_number(stats['kills'])}`")
        if 'muertes' in stats:
            parts.append(f"💀 Muertes: `{self.format_number(stats['deaths'])}`")
        if 'victorias' in stats:
            parts.append(f"🏆 Victorias: `{self.format_number(stats['wins'])}`")
        if 'derrotas' in stats:
            parts.append(f"❌ Derrotas: `{self.format_number(stats['losses'])}`")
        
        return " | ".join(parts)

    def get_rank_color(self, rank):
        rank_colors = {
            "MVP++": 0xFFAA00,
            "MVP+": 0x55FFFF,
            "MVP": 0x55FFFF,
            "VIP+": 0x55FF55,
            "VIP": 0x55FF55,
            "Default": 0x9e9e9e
        }
        return rank_colors.get(rank, 0x9e9e9e)

    @commands.command(name="hypixel")
    async def hypixel(self, ctx, username: str):
        await ctx.defer()
        api_key = os.getenv("HYPIXEL_API")

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
        
        if "hypixel" not in act_commands:
            await ctx.reply("El comando no está activado en este servidor.")
            return

        if not api_key:
            return await ctx.send("❌ API Key de Hypixel no configurada.")

        if username in self.player_profile_cache:
            cached_data = self.player_profile_cache[username]
            if cached_data['timestamp'] > asyncio.get_event_loop().time() - self.CACHE_DURATION:
                return await ctx.send(embed=cached_data['data'])

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"https://api.hypixel.net/player?key={api_key}&name={username}") as resp:
                    player_data = await resp.json()

                if not player_data.get("success") or not player_data.get("player"):
                    return await ctx.send("❌ Jugar no encontrado en Hypixel.")

                player = player_data["player"]
                
                uuid = player.get("uuid", "Unknown")
                display_name = player.get("displayname", "Unknown")
                rank = player.get("newPackageRank", "Default").replace("_", " ").title()
                
                achievement_points = self.format_number(player.get("achievementPoints", "0"))
                karma = self.format_number(player.get("karma", "0"))
                
                first_login = self.format_timestamp(player.get("firstLogin"))
                last_login = self.format_timestamp(player.get("lastLogin"))
                last_logout = self.format_timestamp(player.get("lastLogout"))
                
                skywars = player.get("stats", {}).get("SkyWars", {})
                bedwars = player.get("stats", {}).get("Bedwars", {})
                bedwars_level = player.get("achievements", {}).get("bedwars_level", "0")

                embed = discord.Embed(
                    title=f"📊 Perfil de Hypixel - {display_name}",
                    color=self.get_rank_color(rank)
                )

                embed.set_thumbnail(url=f"https://crafatar.com/renders/body/{uuid}?overlay=true")

                embed.add_field(
                    name="👤 Información básica",
                    value=f"**Rango:** `{rank}`\n"
                          f"**Puntos de logros:** `{achievement_points}`\n"
                          f"**Karma:** `{karma}`\n"
                          f"**Idioma:** `{player.get('userLanguage', 'English')}`",
                    inline=False
                )

                embed.add_field(
                    name="⏰ Información de inicio de sesión",
                    value=f"**Primer inicio de sesión:** {first_login}\n"
                          f"**Último inicio de sesión:** {last_login}\n"
                          f"**Última vez desconexión:** {last_logout}",
                    inline=False
                )

                embed.add_field(
                    name="🗡️ Estadísticas Skywars",
                    value=self.create_stats_string(skywars, include_souls=True),
                    inline=False
                )

                bedwars_stats = {
                    'monedas': bedwars.get('coins', 0),
                    'asesinatos': bedwars.get('kills_bedwars', 0),
                    'muertes': bedwars.get('deaths_bedwars', 0),
                    'victorias': bedwars.get('wins_bedwars', 0),
                    'derrotas': bedwars.get('losses_bedwars', 0)
                }
                
                embed.add_field(
                    name="🛏️ Estadísticas Bedwars",
                    value=f"**Nivel:** `{bedwars_level}`\n{self.create_stats_string(bedwars_stats)}",
                    inline=False
                )

                embed.set_footer(text=f"UUID: {uuid} | Powered by Hypixel API")

                self.player_profile_cache[username] = {
                    "timestamp": asyncio.get_event_loop().time(),
                    "data": embed
                }

                await ctx.send(embed=embed)

            except Exception as e:
                await ctx.send(f"❌ Hubo un error: {str(e)}")

async def setup(bot):
    await bot.add_cog(Hypixel(bot))