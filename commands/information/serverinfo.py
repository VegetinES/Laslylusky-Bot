from database.get import get_specific_field
import discord
from discord import app_commands
from discord.ext import commands
from commands.configuration.configdata import check_command

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="serverinfo")
    async def stats(self, ctx):
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
        
        if "serverinfo" not in act_commands:
            await ctx.reply("El comando no está activado en este servidor.")
            return
        
        server = ctx.guild

        embed = discord.Embed(
            title="**Info Servidor Discord**",
            description="**Información del servidor de Discord**",
            color=discord.Color.random()
        )
        embed.set_thumbnail(url=server.icon.url if server.icon else None)
        embed.set_author(name=server.name, icon_url=server.icon.url if server.icon else None)

        embed.add_field(name="**ID Servidor**", value=server.id, inline=True)
        embed.add_field(name="**Fecha de creación**", value=server.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
        embed.add_field(name="**Creador del servidor:**", value=f"{server.owner}", inline=True)
        embed.add_field(name="**ID Creador:**", value=f"{server.owner_id}", inline=True)

        embed.add_field(
            name=f"**Canales** [{len(server.channels)}]ㅤㅤ",
            value=(
                f"Categoría: {len([c for c in server.channels if isinstance(c, discord.CategoryChannel)])}\n"
                f"Texto: {len([c for c in server.channels if isinstance(c, discord.TextChannel)])}\n"
                f"Voz: {len([c for c in server.channels if isinstance(c, discord.VoiceChannel)])}"
            ),
            inline=True
        )
        embed.add_field(name="**Miembros**", value=server.member_count, inline=True)
        embed.add_field(
            name="**Bots**", 
            value=len([m for m in server.members if m.bot]), 
            inline=True
        )
        embed.add_field(name="**Emojis**", value=len(server.emojis), inline=True)
        embed.add_field(name="**Boosts**", value=server.premium_subscription_count or 0, inline=True)
        embed.add_field(name="**Nivel de Verificación**", value=str(server.verification_level), inline=True)
        embed.add_field(name="**Roles**", value=len(server.roles), inline=True)

        embed.set_footer(
            text=f"Pedido por: {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url
        )

        await ctx.send(embed=embed)
    
    @app_commands.command(name="serverinfo", description="Muestra información detallada del servidor")
    async def stats_slash(self, interaction: discord.Interaction):
        act_commands = get_specific_field(interaction.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if "serverinfo" not in act_commands:
            await interaction.response.send_message("El comando no está activado en este servidor.", ephemeral=True)
            return
        
        server = interaction.guild

        embed = discord.Embed(
            title="**Info Servidor Discord**",
            description="**Información del servidor de Discord**",
            color=discord.Color.random()
        )
        embed.set_thumbnail(url=server.icon.url if server.icon else None)
        embed.set_author(name=server.name, icon_url=server.icon.url if server.icon else None)

        embed.add_field(name="**ID Servidor**", value=server.id, inline=True)
        embed.add_field(name="**Fecha de creación**", value=server.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
        embed.add_field(name="**Creador del servidor:**", value=f"{server.owner}", inline=True)
        embed.add_field(name="**ID Creador:**", value=f"{server.owner_id}", inline=True)

        embed.add_field(
            name=f"**Canales** [{len(server.channels)}]ㅤㅤ",
            value=(
                f"Categoría: {len([c for c in server.channels if isinstance(c, discord.CategoryChannel)])}\n"
                f"Texto: {len([c for c in server.channels if isinstance(c, discord.TextChannel)])}\n"
                f"Voz: {len([c for c in server.channels if isinstance(c, discord.VoiceChannel)])}"
            ),
            inline=True
        )
        embed.add_field(name="**Miembros**", value=server.member_count, inline=True)
        embed.add_field(
            name="**Bots**", 
            value=len([m for m in server.members if m.bot]), 
            inline=True
        )
        embed.add_field(name="**Emojis**", value=len(server.emojis), inline=True)
        embed.add_field(name="**Boosts**", value=server.premium_subscription_count or 0, inline=True)
        embed.add_field(name="**Nivel de Verificación**", value=str(server.verification_level), inline=True)
        embed.add_field(name="**Roles**", value=len(server.roles), inline=True)

        embed.set_footer(
            text=f"Pedido por: {interaction.user.display_name}",
            icon_url=interaction.user.display_avatar.url
        )

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Stats(bot))