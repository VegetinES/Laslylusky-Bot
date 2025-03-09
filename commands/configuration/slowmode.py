from database.get import get_specific_field
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
        
        act_commands = get_specific_field(ctx.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando </config update:1348248454610161751> si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if "slowmode" not in act_commands:
            await ctx.reply("El comando no está activado en este servidor.")
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
