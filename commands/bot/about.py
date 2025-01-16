import discord
from discord.ext import commands

class About(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="about", help="Comando de about")
    async def about(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            return
        
        total_users = len(set(self.bot.get_all_members()))

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
        about_embed.add_field(name="Servidores en los que estoy", value=f"{len(self.bot.guilds)}", inline=False)
        about_embed.add_field(name="Versión", value="vB1.2.0", inline=False)
        about_embed.add_field(name="Comandos", value="56", inline=False)
        about_embed.add_field(name="Usuarios que me ven", value=f"{total_users}", inline=False)
        about_embed.set_footer(
            text=f"Pedido por: {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url
        )

        await ctx.send(embed=about_embed)

async def setup(bot):
    await bot.add_cog(About(bot))