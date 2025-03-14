import discord
from discord.ext import commands
from discord import app_commands
import time
import psutil
import platform
import asyncio
from .help_data import COMMAND_CATEGORIES

class About(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    def get_system_info(self):
        return f"```\nUso de CPU: {psutil.cpu_percent(interval=1)}% \nUso de RAM: {psutil.virtual_memory().percent}% ({round(psutil.virtual_memory().used / (1024 ** 3), 2)}GB/{round(psutil.virtual_memory().total / (1024 ** 3), 2)}GB) \nProcesador: {platform.processor()} \nSO: {platform.system()}\nLatencia: {round(self.bot.latency * 1000, 2)}ms\n```"

    def get_uptime_string(self):
        uptime_seconds = time.time() - self.bot.start_time
        
        days, remainder = divmod(int(uptime_seconds), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m {seconds}s"
        elif hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        else:
            return f"{minutes}m {seconds}s"

    def get_total_users(self):
        return len(set(self.bot.get_all_members()))
    
    async def create_about_embed(self, interaction=None, ctx=None):
        if not hasattr(self.bot, 'start_time'):
            self.bot.start_time = time.time()
            
        total_commands = sum(len(category["commands"]) for category in COMMAND_CATEGORIES.values())

        if interaction:
            user = interaction.user
        else:
            user = ctx.author
            
        about_embed = discord.Embed(
            title="Sobre Laslylusky",
            description=(
                f"Hola <@{user.id}>\n\n"
                "Fui creado por `VegetinES (vegetines)` con el lenguaje Python <:Python:1329365366840758292> en la versión 3.12.3"
            ),
            color=discord.Color.blue()
        )
        about_embed.set_thumbnail(
            url="https://media.discordapp.net/attachments/772803956379222016/1338219290398036042/laslylusky.png"
        )
        
        about_embed.description += self.get_system_info()

        about_embed.add_field(name="Servidores en los que estoy", value=f"{len(self.bot.guilds)}", inline=True)
        about_embed.add_field(name="Versión", value="vB2.1.0", inline=True)
        about_embed.add_field(name="Comandos", value=f"{total_commands}", inline=True)
        about_embed.add_field(name="Usuarios que me ven", value=f"{self.get_total_users()}", inline=True)
        about_embed.add_field(name="Llevo encendido:", value=self.get_uptime_string(), inline=True)
        about_embed.add_field(name="Créditos", value="Tester: itsfoxy23 \nOwner: vegetines", inline=True)

        about_embed.set_footer(
            text=f"Pedido por: {user.display_name}",
            icon_url=user.display_avatar.url
        )
        
        return about_embed

    @commands.command(name="info")
    async def about(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            return

        about_embed = await self.create_about_embed(ctx=ctx)
        message = await ctx.send(embed=about_embed)

        start_time = time.time()
        while time.time() - start_time < 60:
            try:
                new_embed = await self.create_about_embed(ctx=ctx)
                await message.edit(embed=new_embed)
                await asyncio.sleep(1)
                
            except discord.NotFound:
                break
            except Exception as e:
                print(f"Error al actualizar el mensaje: {e}")
                break
    
    @app_commands.command(name="info", description="Muestra información sobre el bot")
    async def about_slash(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        about_embed = await self.create_about_embed(interaction=interaction)
        message = await interaction.followup.send(embed=about_embed, wait=True)
        
        start_time = time.time()
        while time.time() - start_time < 60:
            try:
                new_embed = await self.create_about_embed(interaction=interaction)
                await message.edit(embed=new_embed)
                await asyncio.sleep(1)
                
            except discord.NotFound:
                break
            except Exception as e:
                print(f"Error al actualizar el mensaje: {e}")
                break

async def setup(bot):
    if not hasattr(bot, 'start_time'):
        bot.start_time = time.time()
    await bot.add_cog(About(bot))