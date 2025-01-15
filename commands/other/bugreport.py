import discord
from discord.ext import commands

class BugReport(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="bugreport")
    async def bugreport(self, ctx, *, reporte: str = None):
        if isinstance(ctx.channel, discord.DMChannel):
            return

        if not reporte:
            await ctx.send(f"<@{ctx.author.id}>, escribe un mensaje, por favor.\n\n"
                           f"Escribe el comando que funcione mal o que le falta algo y cuál es el problema.")
            return

        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass

        embed_reporte = discord.Embed(
            title="Reporte de Bug",
            description=f"**Reportado por {ctx.author.display_name}:**\n\n{reporte}",
            color=discord.Color.red(),
            timestamp=ctx.message.created_at
        )
        embed_reporte.set_thumbnail(
            url="https://media.discordapp.net/attachments/818410022907412522/824373373185818704/1616616249024.png?width=593&height=593"
        )
        embed_reporte.set_footer(text=f"ID: {ctx.author.id}", icon_url=ctx.author.avatar.url)

        embed_confirmacion = discord.Embed(
            title=":incoming_envelope: Reporte enviado",
            description=(f"Ey <@{ctx.author.id}>, tu reporte ha sido enviado correctamente al fundador de Laslylusky. "
                         f"¡Muchas gracias por tu colaboración!"),
            color=discord.Color.blue(),
            timestamp=ctx.message.created_at
        )
        embed_confirmacion.set_thumbnail(
            url="https://media.discordapp.net/attachments/818410022907412522/824373373185818704/1616616249024.png?width=593&height=593"
        )
        embed_confirmacion.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar.url)

        canal_reporte_id = 784768523321999390
        canal_reporte = self.bot.get_channel(canal_reporte_id)

        if canal_reporte:
            await canal_reporte.send(embed=embed_reporte)
        else:
            await ctx.send("No se encontró el canal de reportes. Avisa a mi administrador y fundador.")

        await ctx.send(embed=embed_confirmacion)


async def setup(bot):
    await bot.add_cog(BugReport(bot))
