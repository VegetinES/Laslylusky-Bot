from database.get import get_specific_field
import discord
from discord import app_commands
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
    
    @app_commands.command(name="userinfo", description="Muestra información detallada de un usuario")
    @app_commands.describe(usuario="Usuario del que quieres ver la información")
    async def user_slash(self, interaction: discord.Interaction, usuario: discord.User = None):
        act_commands = get_specific_field(interaction.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if "userinfo" not in act_commands:
            await interaction.response.send_message("El comando no está activado en este servidor.", ephemeral=True)
            return

        user = usuario or interaction.user
        member = None
        if isinstance(user, discord.User):
            try:
                member = await interaction.guild.fetch_member(user.id)
            except:
                pass

        target = member or user

        embed = discord.Embed(
            title=f"Información del usuario {target.name}",
            color=0xff8000
        )
        embed.set_thumbnail(url=target.display_avatar.url)

        embed.add_field(
            name="Apodo:",
            value=target.nick if isinstance(target, discord.Member) and target.nick else "No tiene apodo",
            inline=True
        )
        embed.add_field(name="🆔 ID:", value=target.id, inline=False)
        embed.add_field(
            name="Avatar link:",
            value=f"[Pinche Aquí]({target.display_avatar.url})",
            inline=False
        )
        embed.add_field(
            name="Fecha de creación:",
            value=target.created_at.strftime("%Y-%m-%d"),
            inline=True
        )

        if isinstance(target, discord.Member):
            embed.add_field(
                name="Fecha de entrada al servidor:",
                value=target.joined_at.strftime("%Y-%m-%d") if target.joined_at else "Desconocido",
                inline=True
            )
            roles = ", ".join([role.mention for role in target.roles if role.name != "@everyone"])
            embed.add_field(
                name="Roles del usuario:",
                value=roles if roles else "Sin roles",
                inline=True
            )

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(UserInfo(bot))