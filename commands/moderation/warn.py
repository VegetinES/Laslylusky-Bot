import discord
from discord import app_commands
from discord.ext import commands
import time
import datetime
from datetime import datetime
from typing import Union

from database.oracle import Oracle
from database.get import get_specific_field

class Warn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Oracle()

    async def check_custom_permissions(self, ctx):
        perms_data = get_specific_field(ctx.guild.id, "perms")
        if not perms_data:
            return False
        
        if str(ctx.author.id) in perms_data.get("warn-users", []) or str(ctx.author.id) in perms_data.get("admin-users", []):
            return True

        author_role_ids = [str(role.id) for role in ctx.author.roles]
        allowed_warn_roles = perms_data.get("warn-roles", [])
        allowed_admin_roles = perms_data.get("admin-roles", [])
        
        return any(role_id in allowed_warn_roles or role_id in allowed_admin_roles for role_id in author_role_ids)

    async def check_custom_permissions_interaction(self, interaction):
        perms_data = get_specific_field(interaction.guild.id, "perms")
        if not perms_data:
            return False
        
        if str(interaction.user.id) in perms_data.get("warn-users", []) or str(interaction.user.id) in perms_data.get("admin-users", []):
            return True

        author_role_ids = [str(role.id) for role in interaction.user.roles]
        allowed_warn_roles = perms_data.get("warn-roles", [])
        allowed_admin_roles = perms_data.get("admin-roles", [])
        
        return any(role_id in allowed_warn_roles or role_id in allowed_admin_roles for role_id in author_role_ids)

    @app_commands.command(name="warn", description="Sanciona a un usuario")
    @app_commands.describe(
        user="Usuario a sancionar",
        reason="Razón de la sanción (máximo 100 caracteres)"
    )
    @app_commands.default_permissions(moderate_members=True)
    async def slash_warn(self, interaction: discord.Interaction, user: discord.Member, reason: str):
        act_commands = get_specific_field(interaction.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando </config update:1348248454610161751>` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if "warn" not in act_commands:
            await interaction.response.send_message("El comando no está activado en este servidor.", ephemeral=True)
            return

        if len(reason) > 100:
            await interaction.response.send_message("La razón no puede tener más de 100 caracteres.", ephemeral=True)
            return
        
        has_permission = (interaction.user.guild_permissions.moderate_members or 
                         interaction.user.guild_permissions.administrator or 
                         await self.check_custom_permissions_interaction(interaction))
        
        if not has_permission:
            await interaction.response.send_message("No tienes permisos para usar este comando.", ephemeral=True)
            return
        
        if user.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message("No puedes sancionar a un usuario con un rol igual o superior al tuyo.", ephemeral=True)
            return
        
        if user.id == interaction.guild.owner_id:
            await interaction.response.send_message("No puedes sancionar al propietario del servidor.", ephemeral=True)
            return
        
        if user.id == interaction.user.id:
            await interaction.response.send_message("No puedes sancionarte a ti mismo.", ephemeral=True)
            return

        if user.bot:
            await interaction.response.send_message("No puedes sancionar a un bot.", ephemeral=True)
            return

        timestamp = int(time.time())

        try:
            self.db.connect()
            result = self.db.insert(
                guild_id=str(interaction.guild.id),
                user_id=str(user.id),
                mod_id=str(interaction.user.id),
                reason=reason,
                action_type="warn",
                timestamp=timestamp
            )
        except Exception as e:
            await interaction.response.send_message(f"Error al conectar con la base de datos: {str(e)}", ephemeral=True)
            return
        finally:
            self.db.close()
        
        if not result.get("success", False):
            await interaction.response.send_message(f"Error al registrar la sanción: {result.get('error', 'Error desconocido')}", ephemeral=True)
            return
        
        warn_id = result.get("warn_id")

        user_embed = discord.Embed(
            title="⚠️ Has recibido una sanción",
            description=f"Has sido sancionado en el servidor **{interaction.guild.name}**",
            color=discord.Color.red()
        )
        user_embed.add_field(name="Razón", value=reason, inline=False)
        user_embed.add_field(name="Moderador", value=f"{interaction.user.mention} (ID: {interaction.user.id})", inline=False)
        user_embed.add_field(name="ID de Sanción", value=f"`{warn_id}`", inline=False)
        user_embed.timestamp = datetime.fromtimestamp(timestamp)
        user_embed.set_footer(text=f"Servidor: {interaction.guild.name}", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        
        try:
            await user.send(embed=user_embed)
            user_notified = True
        except:
            user_notified = False
        
        mod_embed = discord.Embed(
            title="✅ Sanción aplicada",
            description=f"Se ha aplicado una sanción a {user.mention} por la siguiente razón:\n> {reason}",
            color=discord.Color.green()
        )
        mod_embed.add_field(name="ID de Sanción", value=f"`{warn_id}`", inline=False)
        if not user_notified:
            mod_embed.add_field(name="Nota", value="No se pudo enviar una notificación al usuario.", inline=False)
        mod_embed.timestamp = datetime.fromtimestamp(timestamp)
        
        await interaction.response.send_message(embed=mod_embed, ephemeral=False)

        self.bot.dispatch("warn", 
            interaction.guild.id, 
            str(user.id), 
            user.mention, 
            str(user), 
            reason, 
            str(interaction.user.id), 
            interaction.user.mention, 
            str(interaction.user),
            warn_id
        )
    
    @commands.command(name="warn")
    async def text_warn(self, ctx, user: Union[discord.Member, int], *, reason: str = "No se ha especificado una razón"):
        act_commands = get_specific_field(ctx.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando </config update:1348248454610161751> si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if "warn" not in act_commands:
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

        if isinstance(user, int):
            try:
                user = await ctx.guild.fetch_member(user)
            except discord.NotFound:
                await ctx.reply("No se encontró al usuario con esa ID en el servidor.")
                return

        if len(reason) > 100:
            await ctx.reply("La razón no puede tener más de 100 caracteres.")
            return

        if user.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            await ctx.reply("No puedes sancionar a un usuario con un rol igual o superior al tuyo.")
            return

        if user.id == ctx.guild.owner_id:
            await ctx.reply("No puedes sancionar al propietario del servidor.")
            return

        if user.id == ctx.author.id:
            await ctx.reply("No puedes sancionarte a ti mismo.")
            return

        if user.bot:
            await ctx.reply("No puedes sancionar a un bot.")
            return

        timestamp = int(time.time())

        try:
            self.db.connect()
            result = self.db.insert(
                guild_id=str(ctx.guild.id),
                user_id=str(user.id),
                mod_id=str(ctx.author.id),
                reason=reason,
                action_type="warn",
                timestamp=timestamp
            )
        except Exception as e:
            await ctx.reply(f"Error al conectar con la base de datos: {str(e)}")
            return
        finally:
            self.db.close()

        if not result.get("success", False):
            await ctx.reply(f"Error al registrar la sanción: {result.get('error', 'Error desconocido')}")
            return
        
        warn_id = result.get("warn_id")
        
        user_embed = discord.Embed(
            title="⚠️ Has recibido una sanción",
            description=f"Has sido sancionado en el servidor **{ctx.guild.name}**",
            color=discord.Color.red()
        )
        user_embed.add_field(name="Razón", value=reason, inline=False)
        user_embed.add_field(name="Moderador", value=f"{ctx.author.mention} (ID: {ctx.author.id})", inline=False)
        user_embed.add_field(name="ID de Sanción", value=f"`{warn_id}`", inline=False)
        user_embed.timestamp = datetime.fromtimestamp(timestamp)
        user_embed.set_footer(text=f"Servidor: {ctx.guild.name}", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
        
        try:
            await user.send(embed=user_embed)
            user_notified = True
        except:
            user_notified = False

        mod_embed = discord.Embed(
            title="✅ Sanción aplicada",
            description=f"Se ha aplicado una sanción a {user.mention} por la siguiente razón:\n> {reason}",
            color=discord.Color.green()
        )
        mod_embed.add_field(name="ID de Sanción", value=f"`{warn_id}`", inline=False)
        if not user_notified:
            mod_embed.add_field(name="Nota", value="No se pudo enviar una notificación al usuario.", inline=False)
        mod_embed.timestamp = datetime.fromtimestamp(timestamp)
        
        await ctx.reply(embed=mod_embed)
        
        self.bot.dispatch("warn", 
            ctx.guild.id, 
            str(user.id), 
            user.mention, 
            str(user), 
            reason, 
            str(ctx.author.id), 
            ctx.author.mention, 
            str(ctx.author),
            warn_id
        )

async def setup(bot):
    await bot.add_cog(Warn(bot))