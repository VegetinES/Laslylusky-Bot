import discord
from discord.ext import commands
import time
import psutil
import platform
from .help_data import COMMAND_CATEGORIES

class About(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="info")
    async def about(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            return

        total_users = len(set(self.bot.get_all_members()))
        api_latency = round(self.bot.latency * 1000)

        latency = time.time() - ctx.message.created_at.timestamp()
        if not hasattr(self.bot, 'start_time'):
            self.bot.start_time = time.time()
        uptime_seconds = time.time() - self.bot.start_time
        uptime_string = time.strftime("%H:%M:%S", time.gmtime(uptime_seconds))

        total_commands = sum(len(category["commands"]) for category in COMMAND_CATEGORIES.values())

        os_info = platform.system() + " " + platform.release()
        ram = psutil.virtual_memory()
        ram_usage = f"{ram.used / (1024 ** 3):.2f}GB/{ram.total / (1024 ** 3):.2f}GB"
        cpu = platform.processor()

        about_embed = discord.Embed(
            title="Sobre Laslylusky",
            description=(
                f"Hola <@{ctx.author.id}>\n\n"
                "Fui creado por `VegetinES (vegetines)` con el lenguaje Python <:Python:1329365366840758292>"
            ),
            color=discord.Color.random()
        )
        about_embed.set_thumbnail(
            url="https://media.discordapp.net/attachments/818410022907412522/824373373185818704/1616616249024.png?width=593&height=593"
        )
        about_embed.add_field(name="Servidores en los que estoy", value=f"{len(self.bot.guilds)}", inline=True)
        about_embed.add_field(name="Versión", value="vB1.3.0", inline=True)
        about_embed.add_field(name="Comandos", value=f"{total_commands}", inline=True)
        about_embed.add_field(name="Usuarios que me ven", value=f"{total_users}", inline=True)
        about_embed.add_field(name="Mi latencia es:", value=f"{latency * 1000:.2f}ms", inline=True)
        about_embed.add_field(name="La latencia de mi API es:", value=f"{api_latency}ms", inline=True)
        about_embed.add_field(name="Llevo encendido:", value=uptime_string, inline=True)

        about_embed.add_field(name="Sistema Operativo", value=os_info, inline=True)
        about_embed.add_field(name="RAM", value=ram_usage, inline=True)
        about_embed.add_field(name="CPU", value=cpu, inline=True)

        about_embed.set_footer(
            text=f"Pedido por: {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url
        )

        await ctx.send(embed=about_embed)

async def setup(bot):
    if not hasattr(bot, 'start_time'):
        bot.start_time = time.time()
    await bot.add_cog(About(bot)) 
