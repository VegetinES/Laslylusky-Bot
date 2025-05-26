import discord
from discord.ext import commands
from discord import app_commands
import re
import asyncio
import datetime
from database.get import get_specific_field

class Isolate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.time_pattern = re.compile(r'^(\d+)([smhd])$')
        self.max_isolate_days = 7

    async def check_custom_permissions(self, ctx):
        perms_data = get_specific_field(ctx.guild.id, "perms")
        if not perms_data:
            return False
        
        if str(ctx.author.id) in perms_data.get("mute-users", []) or str(ctx.author.id) in perms_data.get("admin-users", []):
            return True

        author_role_ids = [str(role.id) for role in ctx.author.roles]
        allowed_mute_roles = perms_data.get("mute-roles", [])
        allowed_admin_roles = perms_data.get("admin-roles", [])
        
        return any(role_id in allowed_mute_roles or role_id in allowed_admin_roles for role_id in author_role_ids)
    
    async def check_custom_permissions_interaction(self, interaction):
        perms_data = get_specific_field(interaction.guild.id, "perms")
        if not perms_data:
            return False
        
        if str(interaction.user.id) in perms_data.get("mute-users", []) or str(interaction.user.id) in perms_data.get("admin-users", []):
            return True

        author_role_ids = [str(role.id) for role in interaction.user.roles]
        allowed_mute_roles = perms_data.get("mute-roles", [])
        allowed_admin_roles = perms_data.get("admin-roles", [])
        
        return any(role_id in allowed_mute_roles or role_id in allowed_admin_roles for role_id in author_role_ids)

    def parse_time(self, time_str):
        if not time_str:
            return None, "Debes especificar un tiempo de aislamiento."
        
        match = self.time_pattern.match(time_str)
        if not match:
            return None, "Formato de tiempo incorrecto. Usa formato: número+s/m/h/d. Ejemplo: 1d, 5h, 30m, 10s"
        
        value, unit = match.groups()
        value = int(value)
        
        if value <= 0:
            return None, "El tiempo debe ser mayor a 0."
        
        if unit == 's':
            seconds = value
            time_text = f"{value} segundo{'s' if value != 1 else ''}"
        elif unit == 'm':
            seconds = value * 60
            time_text = f"{value} minuto{'s' if value != 1 else ''}"
        elif unit == 'h':
            seconds = value * 3600
            time_text = f"{value} hora{'s' if value != 1 else ''}"
        elif unit == 'd':
            seconds = value * 86400
            time_text = f"{value} día{'s' if value != 1 else ''}"
        else:
            return None, "Unidad de tiempo no válida. Usa s (segundos), m (minutos), h (horas) o d (días)."

        max_seconds = self.max_isolate_days * 86400
        if seconds > max_seconds:
            return None, f"El tiempo máximo de aislamiento es de {self.max_isolate_days} días."
        
        return seconds, time_text

    @commands.command(name="mute")
    async def aislar(self, ctx, member: discord.Member = None, time_str: str = None, *, reason: str = None):
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
        
        if "mute" not in act_commands:
            await ctx.reply("El comando no está activado en este servidor.")
            return

        has_permission = (ctx.author.guild_permissions.moderate_members or 
                         ctx.author.guild_permissions.administrator or 
                         await self.check_custom_permissions(ctx))
        
        if not has_permission:
            embed = discord.Embed(
                title="**No tienes permiso para usar este comando**",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if not ctx.guild.me.guild_permissions.moderate_members:
            await ctx.reply("No tengo permisos para aislar usuarios en este servidor.")
            return

        if member is None:
            await ctx.reply("Debes mencionar a un usuario para aislar.")
            return
            
        if time_str is None:
            await ctx.reply("Debes especificar un tiempo de aislamiento (ejemplos: 30s, 5m, 2h, 1d).")
            return
            
        if member.id == ctx.author.id:
            await ctx.reply("No puedes aislarte a ti mismo.")
            return
            
        if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            await ctx.reply("No puedes aislar a alguien con un rol igual o superior al tuyo.")
            return
            
        if member.top_role >= ctx.guild.me.top_role:
            await ctx.reply("No puedo aislar a alguien con un rol superior al mío.")
            return
            
        if member.id == ctx.guild.owner_id:
            await ctx.reply("No puedo aislar al propietario del servidor.")
            return

        seconds, time_text = self.parse_time(time_str)
        if seconds is None:
            await ctx.reply(time_text)
            return

        isolation_reason = reason if reason else f"Aislado por {ctx.author.name}"

        try:
            embed = discord.Embed(
                title="⚠️ Has sido Aislado",
                color=discord.Color.orange()
            )
            embed.add_field(name="Servidor:", value=ctx.guild.name, inline=False)
            embed.add_field(name="Moderador:", value=ctx.author.name, inline=False)
            embed.add_field(name="Duración:", value=time_text, inline=False)
            embed.add_field(name="Razón:", value=isolation_reason, inline=False)
            embed.set_footer(text=f"Aislado por: {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
            embed.timestamp = discord.utils.utcnow()
            
            try:
                await member.send(embed=embed)
            except discord.Forbidden:
                await ctx.send("No pude enviar un mensaje directo al usuario, aislándolo de todas formas.")

            until = discord.utils.utcnow() + datetime.timedelta(seconds=seconds)
            await member.timeout(until, reason=isolation_reason)
            
            confirmation = discord.Embed(
                title="✅ Usuario Aislado",
                color=discord.Color.orange()
            )
            confirmation.add_field(name="Usuario:", value=f"{member.name} ({member.id})", inline=False)
            confirmation.add_field(name="Moderador:", value=f"{ctx.author.name} ({ctx.author.id})", inline=False)
            confirmation.add_field(name="Duración:", value=time_text, inline=False)
            confirmation.add_field(name="Razón:", value=isolation_reason, inline=False)
            confirmation.set_footer(text=f"Aislado por: {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
            confirmation.timestamp = discord.utils.utcnow()

            await ctx.send(embed=confirmation)
        
        except discord.Forbidden:
            await ctx.reply("No tengo permisos para aislar a ese usuario.")
        except Exception as e:
            await ctx.reply(f"Ocurrió un error al intentar aislar al usuario: {e}")

    @app_commands.command(name="mute", description="Aisla temporalmente a un usuario del servidor")
    @app_commands.describe(
        usuario="Usuario a aislar",
        tiempo="Duración del aislamiento (s para segundos, m para minutos, h para horas, d para días). Ejemplo: 1d",
        razon="Razón del aislamiento"
    )
    @app_commands.default_permissions(moderate_members=True)
    async def slash_aislar(self, interaction: discord.Interaction, usuario: discord.Member, tiempo: str, razon: str = None):
        act_commands = get_specific_field(interaction.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if "mute" not in act_commands:
            await interaction.response.send_message("El comando no está activado en este servidor.", ephemeral=True)
            return
        
        has_permission = (interaction.user.guild_permissions.moderate_members or 
                         interaction.user.guild_permissions.administrator or 
                         await self.check_custom_permissions_interaction(interaction))
        
        if not has_permission:
            embed = discord.Embed(
                title="**No tienes permiso para usar este comando**",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if not interaction.guild.me.guild_permissions.moderate_members:
            await interaction.response.send_message("No tengo permisos para aislar usuarios en este servidor.", ephemeral=True)
            return

        if usuario.id == interaction.user.id:
            await interaction.response.send_message("No puedes aislarte a ti mismo.", ephemeral=True)
            return
            
        if usuario.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message("No puedes aislar a alguien con un rol igual o superior al tuyo.", ephemeral=True)
            return
            
        if usuario.top_role >= interaction.guild.me.top_role:
            await interaction.response.send_message("No puedo aislar a alguien con un rol superior al mío.", ephemeral=True)
            return
            
        if usuario.id == interaction.guild.owner_id:
            await interaction.response.send_message("No puedo aislar al propietario del servidor.", ephemeral=True)
            return

        seconds, time_text = self.parse_time(tiempo)
        if seconds is None:
            await interaction.response.send_message(time_text, ephemeral=True)
            return

        isolation_reason = razon if razon else f"Aislado por {interaction.user.name}"

        await interaction.response.defer()
        
        try:
            embed = discord.Embed(
                title="⚠️ Has sido Aislado",
                color=discord.Color.orange()
            )
            embed.add_field(name="Servidor:", value=interaction.guild.name, inline=False)
            embed.add_field(name="Moderador:", value=interaction.user.name, inline=False)
            embed.add_field(name="Duración:", value=time_text, inline=False)
            embed.add_field(name="Razón:", value=isolation_reason, inline=False)
            embed.set_footer(text=f"Aislado por: {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
            embed.timestamp = discord.utils.utcnow()
            
            try:
                await usuario.send(embed=embed)
            except discord.Forbidden:
                pass

            until = discord.utils.utcnow() + datetime.timedelta(seconds=seconds)
            await usuario.timeout(until, reason=isolation_reason)
            
            confirmation = discord.Embed(
                title="✅ Usuario Aislado",
                color=discord.Color.orange()
            )
            confirmation.add_field(name="Usuario:", value=f"{usuario.name} ({usuario.id})", inline=False)
            confirmation.add_field(name="Moderador:", value=f"{interaction.user.name} ({interaction.user.id})", inline=False)
            confirmation.add_field(name="Duración:", value=time_text, inline=False)
            confirmation.add_field(name="Razón:", value=isolation_reason, inline=False)
            confirmation.set_footer(text=f"Aislado por: {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
            confirmation.timestamp = discord.utils.utcnow()

            await interaction.followup.send(embed=confirmation)
        
        except discord.Forbidden:
            await interaction.followup.send("No tengo permisos para aislar a ese usuario.")
        except Exception as e:
            await interaction.followup.send(f"Ocurrió un error al intentar aislar al usuario: {e}")

async def setup(bot):
    await bot.add_cog(Isolate(bot))