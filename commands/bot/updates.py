import discord
from discord.ext import commands
from discord import app_commands
from .updates_data import UPDATES_INFO

class Updates(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def create_general_embed(self, user):
        embed = discord.Embed(
            title="Actualizaciones del bot",
            description="Escribe `%update {versión}` para saber la actualización de esa versión. **Recuerda no escribir `{}`** \n\nSustituye `{versión}` por una de las siguientes versiones.",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/772803956379222016/1338219290398036042/laslylusky.png")
        
        versions_str = "` | `".join(UPDATES_INFO["versions"])
        embed.add_field(name="Actualizaciones Disponibles", value=f"`{versions_str}`")
        
        embed.set_footer(text=f"Pedido por: {user.display_name}", icon_url=user.avatar.url)
        return embed

    def create_version_embed(self, user, version):
        if version not in UPDATES_INFO["details"]:
            return None

        version_info = UPDATES_INFO["details"][version]
        embed = discord.Embed(
            title=version_info["title"],
            description=version_info["content"],
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Pedido por: {user.display_name}", icon_url=user.avatar.url)
        return embed

    @commands.command(name='updates')
    async def update_command(self, ctx, version: str = None):
        if isinstance(ctx.channel, discord.DMChannel):
            return

        if not version:
            embed = self.create_general_embed(ctx.author)
            await ctx.send(embed=embed)
            return

        embed = self.create_version_embed(ctx.author, version)
        if embed:
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"La versión `{version}` no se encuentra en la lista de actualizaciones.")
    
    async def version_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        versions = UPDATES_INFO["versions"]
        return [
            app_commands.Choice(name=version, value=version)
            for version in versions if current.lower() in version.lower()
        ][:25]
    
    @app_commands.command(name="updates", description="Muestra las actualizaciones del bot")
    @app_commands.describe(
        version="La versión específica de la que quieres obtener información"
    )
    @app_commands.autocomplete(version=version_autocomplete)
    async def updates_slash(self, interaction: discord.Interaction, version: str = None):
        if not version:
            embed = self.create_general_embed(interaction.user)
            await interaction.response.send_message(embed=embed)
            return
        
        embed = self.create_version_embed(interaction.user, version)
        if embed:
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f"La versión `{version}` no se encuentra en la lista de actualizaciones.")

async def setup(bot):
    await bot.add_cog(Updates(bot))