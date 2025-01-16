import discord
from discord.ext import commands
from .updates_data import UPDATES_INFO

class Updates(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def create_general_embed(self, ctx):
        user = ctx.author

        embed = discord.Embed(
            title="Actualizaciones del bot",
            description="Escribe `%update {versión}` para saber la actualización de esa versión. **Recuerda no escribir `{}`** \n\nSustituye `{versión}` por una de las siguientes versiones.",
            color=discord.Color.random()
        )
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/818410022907412522/824373373185818704/1616616249024.png?width=593&height=593")
        
        versions_str = "` | `".join(UPDATES_INFO["versions"])
        embed.add_field(name="Actualizaciones Disponibles", value=f"`{versions_str}`")
        
        embed.set_footer(text=f"Pedido por: {user.display_name}", icon_url=user.avatar.url)
        return embed

    def create_version_embed(self, ctx, version):
        user = ctx.author

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
            embed = self.create_general_embed(ctx)
            await ctx.send(embed=embed)
            return

        embed = self.create_version_embed(ctx, version)
        if embed:
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"La versión `{version}` no se encuentra en la lista de actualizaciones.")

async def setup(bot):
    await bot.add_cog(Updates(bot))
