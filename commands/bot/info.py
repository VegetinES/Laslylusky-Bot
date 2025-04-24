import discord
from discord.ext import commands
from discord import app_commands
import time
import psutil
import platform
import asyncio
from .help_data import COMMAND_CATEGORIES

class RefreshButton(discord.ui.View):
    def __init__(self, cog, interaction=None, ctx=None, timeout=60.0):
        super().__init__(timeout=timeout)
        self.cog = cog
        self.interaction = interaction
        self.ctx = ctx
        self.message = None
    
    @discord.ui.button(label="Actualizar", style=discord.ButtonStyle.primary, emoji="🔄")
    async def refresh_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        new_embed = await self.cog.create_about_embed(interaction=interaction)
        await interaction.response.edit_message(embed=new_embed, view=self)
    
    async def on_timeout(self):
        try:
            if self.message:
                await self.message.edit(view=None)
        except discord.NotFound:
            pass
        except Exception as e:
            print(f"Error al eliminar los botones tras timeout: {e}")

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
        about_embed.add_field(name="Versión", value="vB2.4.0", inline=True)
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
        view = RefreshButton(self, ctx=ctx)
        message = await ctx.send(embed=about_embed, view=view)
        view.message = message

    @app_commands.command(name="info", description="Muestra información sobre el bot")
    async def about_slash(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        about_embed = await self.create_about_embed(interaction=interaction)
        view = RefreshButton(self, interaction=interaction)
        message = await interaction.followup.send(embed=about_embed, view=view, wait=True)
        view.message = message

async def setup(bot):
    if not hasattr(bot, 'start_time'):
        bot.start_time = time.time()
    await bot.add_cog(About(bot))