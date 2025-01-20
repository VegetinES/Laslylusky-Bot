import discord
from discord.ext import commands

class Suggest(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="bot-suggest")
    async def suggest(self, ctx, *, sugerencia: str = None):
        if isinstance(ctx.channel, discord.DMChannel):
            return

        if not sugerencia:
            await ctx.send("Escribe una sugerencia, por favor.")
            return

        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass

        embed_sugerencia = discord.Embed(
            title="Nueva Sugerencia",
            description=f"Sugerencia de {ctx.author.display_name}:\n\n{sugerencia}",
            color=discord.Color.blue(),
            timestamp=ctx.message.created_at
        )
        embed_sugerencia.set_thumbnail(
            url="https://media.discordapp.net/attachments/772803956379222016/1329014967239839744/2cef87cccba0f00826a16740ac049231.png?ex=6788cd24&is=67877ba4&hm=72e8520e7b4654280d6cadf0ac23cec37de06f70eaaa647cc6a87883401569c0&=&format=webp&quality=lossless"
        )
        embed_sugerencia.set_footer(text=f"ID: {ctx.author.id}", icon_url=ctx.author.avatar.url)

        embed_confirmacion = discord.Embed(
            title="Sugerencia enviada",
            description=(f"Ey {ctx.author.mention}, tu sugerencia ha sido enviada correctamente. "
                         f"Puedes verla en el canal de sugerencias correspondiente."),
            color=discord.Color.blue(),
            timestamp=ctx.message.created_at
        )
        embed_confirmacion.set_thumbnail(
            url="https://media.discordapp.net/attachments/772803956379222016/1329014967239839744/2cef87cccba0f00826a16740ac049231.png?ex=6788cd24&is=67877ba4&hm=72e8520e7b4654280d6cadf0ac23cec37de06f70eaaa647cc6a87883401569c0&=&format=webp&quality=lossless"
        )
        embed_confirmacion.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar.url)

        canal_sugerencias_id = 784768516258660352
        canal_sugerencias = self.bot.get_channel(canal_sugerencias_id)

        if canal_sugerencias:
            mensaje = await canal_sugerencias.send(embed=embed_sugerencia)
            await mensaje.add_reaction("✅")
            await mensaje.add_reaction("❌")

            try:
                await ctx.author.send(embed=embed_confirmacion)
            except discord.Forbidden:
                await ctx.send(f"{ctx.author.mention}, no pude enviarte un mensaje directo. Aquí tienes la confirmación:",
                               embed=embed_confirmacion)
        else:
            await ctx.send("No se encontró el canal de sugerencias. Avisa a mi administrador y fundador.")

async def setup(bot):
    await bot.add_cog(Suggest(bot))