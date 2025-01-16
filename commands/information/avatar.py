import discord
from discord.ext import commands

class Avatar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="avatar")
    async def avatar(self, ctx, *args):
        if isinstance(ctx.channel, discord.DMChannel):
            return

        user = None

        if ctx.message.mentions:
            user = ctx.message.mentions[0]
        elif args:
            try:
                user = await self.bot.fetch_user(args[0])
            except discord.NotFound:
                await ctx.send("No se encontró el usuario con ese ID.")
                return
        else:
            user = ctx.author

        avatar_url = user.display_avatar.url

        embed = discord.Embed(
            title=f"El avatar de {user}",
            description=f"[URL del avatar de {user}]({avatar_url})",
            color=0x1d1d1d
        )
        embed.set_image(url=avatar_url)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Avatar(bot))
