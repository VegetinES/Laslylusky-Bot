import discord
from discord.ext import commands
from database.get import get_specific_field

class EmbedCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="embed")
    async def embed(self, ctx, *, mensaje: str = None):
        if isinstance(ctx.channel, discord.DMChannel):
            return
        
        act_commands = get_specific_field(ctx.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el servidor o habilita algún comando",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if "embed" not in act_commands:
            await ctx.reply("El comando no está activado en este servidor.")
            return
        
        if not mensaje:
            await ctx.send("Por favor, escribe un mensaje")
            return

        await ctx.message.delete()

        embed = discord.Embed(
            description=mensaje,
            color=discord.Color.random()
        )

        embed.set_footer(
            text=f"Enviado por: {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url
        )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(EmbedCommand(bot))