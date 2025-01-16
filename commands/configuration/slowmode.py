import discord
from discord.ext import commands

class SlowMode(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="slowmode")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, duration: int = None, *, reason: str = None):
        if isinstance(ctx.channel, discord.DMChannel):
            return

        if duration is None or duration < 0:
            await ctx.reply("Por favor, especifica un tiempo válido en segundos.")
            return

        if not reason:
            await ctx.reply("Por favor, especifica una razón.")
            return

        try:
            await ctx.channel.edit(slowmode_delay=duration, reason=reason)
            await ctx.reply(f"Se ha cambiado el cooldown de este canal a {duration} segundos por: {reason}")
        except discord.Forbidden:
            await ctx.reply("No tengo permisos para cambiar el slowmode de este canal.")
        except discord.HTTPException as e:
            await ctx.reply(f"Ocurrió un error al intentar cambiar el slowmode: {e}")

async def setup(bot):
    await bot.add_cog(SlowMode(bot))
