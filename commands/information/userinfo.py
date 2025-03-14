from database.get import get_specific_field
import discord
from discord.ext import commands

class UserInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="userinfo")
    async def user(self, ctx, *, member: discord.Member = None):
        if isinstance(ctx.channel, discord.DMChannel):
            return
        
        act_commands = get_specific_field(ctx.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if "userinfo" not in act_commands:
            await ctx.reply("El comando no está activado en este servidor.")
            return

        user = member or ctx.author

        embed = discord.Embed(
            title=f"Información del usuario {user.name}",
            color=0xff8000
        )
        embed.set_thumbnail(url=user.display_avatar.url)

        embed.add_field(
            name="Apodo:",
            value=user.nick if isinstance(user, discord.Member) and user.nick else "No tiene apodo",
            inline=True
        )
        embed.add_field(name="🆔 ID:", value=user.id, inline=False)
        embed.add_field(
            name="Avatar link:",
            value=f"[Pinche Aquí]({user.display_avatar.url})",
            inline=False
        )
        embed.add_field(
            name="Fecha de creación:",
            value=user.created_at.strftime("%Y-%m-%d"),
            inline=True
        )

        if isinstance(user, discord.Member):
            embed.add_field(
                name="Fecha de entrada al servidor:",
                value=user.joined_at.strftime("%Y-%m-%d") if user.joined_at else "Desconocido",
                inline=True
            )
            roles = ", ".join([role.mention for role in user.roles if role.name != "@everyone"])
            embed.add_field(
                name="Roles del usuario:",
                value=roles if roles else "Sin roles",
                inline=True
            )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(UserInfo(bot))