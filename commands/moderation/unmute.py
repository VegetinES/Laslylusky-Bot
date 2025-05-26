import discord
from discord.ext import commands
from discord import app_commands
from database.get import get_specific_field

class Unisolate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
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

    @commands.command(name="unmute")
    async def desaislar(self, ctx, member: discord.Member = None, *, reason: str = None):
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
        
        if "unmute" not in act_commands:
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
            await ctx.reply("No tengo permisos para desaislar usuarios en este servidor.")
            return

        if member is None:
            await ctx.reply("Debes mencionar a un usuario para desaislar.")
            return
            
        if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            await ctx.reply("No puedes desaislar a alguien con un rol igual o superior al tuyo.")
            return
            
        if member.top_role >= ctx.guild.me.top_role:
            await ctx.reply("No puedo desaislar a alguien con un rol superior al mío.")
            return

        if member.timed_out_until is None or member.timed_out_until < discord.utils.utcnow():
            await ctx.reply("Este usuario no está aislado actualmente.")
            return

        unisolation_reason = reason if reason else f"Desaislado por {ctx.author.name}"

        try:
            embed = discord.Embed(
                title="🔓 Has sido Desaislado",
                color=discord.Color.green()
            )
            embed.add_field(name="Servidor:", value=ctx.guild.name, inline=False)
            embed.add_field(name="Moderador:", value=ctx.author.name, inline=False)
            embed.add_field(name="Razón:", value=unisolation_reason, inline=False)
            embed.set_footer(text=f"Desaislado por: {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
            embed.timestamp = discord.utils.utcnow()
            
            try:
                await member.send(embed=embed)
            except discord.Forbidden:
                await ctx.send("No pude enviar un mensaje directo al usuario, desaislándolo de todas formas.")

            await member.timeout(None, reason=unisolation_reason)
            
            confirmation = discord.Embed(
                title="✅ Usuario Desaislado",
                color=discord.Color.green()
            )
            confirmation.add_field(name="Usuario:", value=f"{member.name} ({member.id})", inline=False)
            confirmation.add_field(name="Moderador:", value=f"{ctx.author.name} ({ctx.author.id})", inline=False)
            confirmation.add_field(name="Razón:", value=unisolation_reason, inline=False)
            confirmation.set_footer(text=f"Desaislado por: {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
            confirmation.timestamp = discord.utils.utcnow()

            await ctx.send(embed=confirmation)
        
        except discord.Forbidden:
            await ctx.reply("No tengo permisos para desaislar a ese usuario.")
        except Exception as e:
            await ctx.reply(f"Ocurrió un error al intentar desaislar al usuario: {e}")

    @app_commands.command(name="unmute", description="Remueve el aislamiento a un usuario")
    @app_commands.describe(
        usuario="Usuario a desaislar",
        razon="Razón del desaislamiento"
    )
    @app_commands.default_permissions(moderate_members=True)
    async def slash_desaislar(self, interaction: discord.Interaction, usuario: discord.Member, razon: str = None):
        act_commands = get_specific_field(interaction.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if "unmute" not in act_commands:
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
            await interaction.response.send_message("No tengo permisos para desaislar usuarios en este servidor.", ephemeral=True)
            return
            
        if usuario.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message("No puedes desaislar a alguien con un rol igual o superior al tuyo.", ephemeral=True)
            return
            
        if usuario.top_role >= interaction.guild.me.top_role:
            await interaction.response.send_message("No puedo desaislar a alguien con un rol superior al mío.", ephemeral=True)
            return

        if usuario.timed_out_until is None or usuario.timed_out_until < discord.utils.utcnow():
            await interaction.response.send_message("Este usuario no está aislado actualmente.", ephemeral=True)
            return

        unisolation_reason = razon if razon else f"Desaislado por {interaction.user.name}"

        await interaction.response.defer()
        
        try:
            embed = discord.Embed(
                title="🔓 Has sido Desaislado",
                color=discord.Color.green()
            )
            embed.add_field(name="Servidor:", value=interaction.guild.name, inline=False)
            embed.add_field(name="Moderador:", value=interaction.user.name, inline=False)
            embed.add_field(name="Razón:", value=unisolation_reason, inline=False)
            embed.set_footer(text=f"Desaislado por: {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
            embed.timestamp = discord.utils.utcnow()
            
            try:
                await usuario.send(embed=embed)
            except discord.Forbidden:
                pass

            await usuario.timeout(None, reason=unisolation_reason)
            
            confirmation = discord.Embed(
                title="✅ Usuario Desaislado",
                color=discord.Color.green()
            )
            confirmation.add_field(name="Usuario:", value=f"{usuario.name} ({usuario.id})", inline=False)
            confirmation.add_field(name="Moderador:", value=f"{interaction.user.name} ({interaction.user.id})", inline=False)
            confirmation.add_field(name="Razón:", value=unisolation_reason, inline=False)
            confirmation.set_footer(text=f"Desaislado por: {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
            confirmation.timestamp = discord.utils.utcnow()

            await interaction.followup.send(embed=confirmation)
        
        except discord.Forbidden:
            await interaction.followup.send("No tengo permisos para desaislar a ese usuario.")
        except Exception as e:
            await interaction.followup.send(f"Ocurrió un error al intentar desaislar al usuario: {e}")

async def setup(bot):
    await bot.add_cog(Unisolate(bot))