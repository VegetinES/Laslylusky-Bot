import discord
from discord.ext import commands

class Invite(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="invite")
    async def invite(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            return

        embed_invite = discord.Embed(
            title="Invitar al bot",
            description=(
                f"Hola <@{ctx.author.id}>. Puedes invitarme de dos formas:\n\n"
                "- **Invitar al bot para utilizar solo los comandos generales, diversión, información, algunos de utilidad, interacción, anime, minecraft y juegos** "
                "[invitación](https://discord.com/oauth2/authorize?client_id=784774864766500864&scope=bot%20applications.commands&permissions=3525697)\n\n"
                "- **Invitar al bot para utilizar todos los comandos (recomendable)** "
                "[invitación](https://discord.com/oauth2/authorize?client_id=784774864766500864&scope=bot%20applications.commands&permissions=8589803519)"
            ),
            color=discord.Color.random()
        )
        embed_invite.set_thumbnail(
            url="https://media.discordapp.net/attachments/818410022907412522/824373373185818704/1616616249024.png?width=593&height=593"
        )
        embed_invite.set_footer(
            text=f"Pedido por: {ctx.author.display_name}",
            icon_url=ctx.author.avatar.url
        )

        try:
            await ctx.author.send(embed=embed_invite)
        except discord.Forbidden:
            await ctx.send(
                f"No te lo he podido enviar por MD, pero aquí tienes la invitación al servidor:",
                embed=embed_invite
            )

async def setup(bot):
    await bot.add_cog(Invite(bot))
