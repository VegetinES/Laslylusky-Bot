from database.get import get_specific_field
import discord
from discord.ext import commands

class Avatar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="avatar")
    async def avatar(self, ctx, *args):
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
        
        if "avatar" not in act_commands:
            await ctx.reply("El comando no está activado en este servidor.")
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
