import discord
from discord.ext import commands
from discord import app_commands
from database.get import get_specific_field
from logs.kicklogs import send_kick_log

class Kick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def check_custom_permissions(self, ctx):
        perms_data = get_specific_field(ctx.guild.id, "perms")
        if not perms_data:
            return False
        
        if str(ctx.author.id) in perms_data.get("kick-users", []) or str(ctx.author.id) in perms_data.get("admin-users", []):
            return True

        author_role_ids = [str(role.id) for role in ctx.author.roles]
        allowed_msg_roles = perms_data.get("kick-roles", [])
        allowed_admin_roles = perms_data.get("admin-roles", [])
        
        return any(role_id in allowed_msg_roles or role_id in allowed_admin_roles for role_id in author_role_ids)

    async def check_custom_permissions_interaction(self, interaction):
        perms_data = get_specific_field(interaction.guild.id, "perms")
        if not perms_data:
            return False
        
        if str(interaction.user.id) in perms_data.get("kick-users", []) or str(interaction.user.id) in perms_data.get("admin-users", []):
            return True

        author_role_ids = [str(role.id) for role in interaction.user.roles]
        allowed_kick_roles = perms_data.get("kick-roles", [])
        allowed_admin_roles = perms_data.get("admin-roles", [])
        
        return any(role_id in allowed_kick_roles or role_id in allowed_admin_roles for role_id in author_role_ids)

    @commands.command(name="kick")
    async def kick(self, ctx, member: discord.Member = None, *, reason: str = None):
        try:
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

            if "kick" not in act_commands:
                await ctx.reply("El comando no está activado en este servidor.")
                return

            has_permission = (ctx.author.guild_permissions.kick_members or 
                            ctx.author.guild_permissions.administrator or 
                            await self.check_custom_permissions(ctx))
            
            if not has_permission:
                embed = discord.Embed(
                    title="**No tienes permiso para usar este comando**",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return

            if member is None:
                await ctx.reply("Menciona al usuario, usa su ID o su nombre de usuario.")
                return

            try:
                member = await ctx.guild.fetch_member(member.id)
            except:
                await ctx.reply("No pude encontrar al usuario en el servidor.")
                return

            if member.id == ctx.author.id:
                await ctx.reply("No puedes expulsarte a ti mismo.")
                return

            if member.id == self.bot.user.id:
                await ctx.reply("No me puedes expulsar.")
                return

            bot_member = ctx.guild.me
            if not ctx.guild.me.guild_permissions.kick_members:
                await ctx.reply("No tengo permisos para expulsar usuarios.")
                return

            if member.top_role >= bot_member.top_role:
                await ctx.reply("No puedo expulsar a este usuario. Mi rol debe estar por encima del suyo.")
                return

            if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
                await ctx.reply("No puedes expulsar a alguien con un rol igual o superior al tuyo.")
                return

            kick_reason = reason if reason else f"Expulsado por {ctx.author.name}"

            try:
                embed = discord.Embed(
                    title="⚠️ Has sido Expulsado",
                    color=discord.Color.orange()
                )
                embed.add_field(name="Servidor:", value=ctx.guild.name, inline=False)
                embed.add_field(name="Moderador:", value=ctx.author.name, inline=False)
                embed.add_field(name="Razón:", value=kick_reason, inline=False)
                embed.set_footer(text=f"Expulsado por: {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
                embed.timestamp = discord.utils.utcnow()
                
                await member.send(embed=embed)
            except:
                await ctx.send("No pude enviar un MD al usuario, procediendo con la expulsión...")

            await member.kick(reason=kick_reason)
            
            confirmation = discord.Embed(
                title="✅ Usuario Expulsado",
                color=discord.Color.orange()
            )
            confirmation.add_field(name="Usuario:", value=f"{member.name} ({member.id})", inline=False)
            confirmation.add_field(name="Moderador:", value=f"{ctx.author.name} ({ctx.author.id})", inline=False)
            confirmation.add_field(name="Razón:", value=kick_reason, inline=False)
            confirmation.set_footer(text=f"Expulsado por: {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
            confirmation.timestamp = discord.utils.utcnow()

            await ctx.send(embed=confirmation)

            await send_kick_log(
                self.bot,
                guild=ctx.guild,
                target=member,
                moderator=ctx.author,
                reason=kick_reason,
                source="command"
            )
        
        except discord.NotFound:
            await ctx.reply("No se encontró ningún usuario con esa ID.")
        except discord.Forbidden:
            await ctx.reply("No tengo permisos para expulsar a ese usuario.")
        except discord.HTTPException as e:
            await ctx.reply(f"Ocurrió un error al intentar expulsar al usuario: {e}")

    @app_commands.command(name="kick", description="Expulsa a un usuario del servidor")
    @app_commands.describe(
        usuario="Usuario a expulsar",
        razon="Razón de la expulsión"
    )
    @app_commands.default_permissions(kick_members=True)
    async def slash_kick(self, interaction: discord.Interaction, usuario: discord.Member, razon: str = None):
        try:
            act_commands = get_specific_field(interaction.guild.id, "act_cmd")
            if act_commands is None:
                embed = discord.Embed(
                    title="<:No:825734196256440340> Error de Configuración",
                    description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            if "kick" not in act_commands:
                await interaction.response.send_message("El comando no está activado en este servidor.", ephemeral=True)
                return

            has_permission = (interaction.user.guild_permissions.kick_members or 
                            interaction.user.guild_permissions.administrator or 
                            await self.check_custom_permissions_interaction(interaction))
            
            if not has_permission:
                embed = discord.Embed(
                    title="**No tienes permiso para usar este comando**",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            try:
                usuario = await interaction.guild.fetch_member(usuario.id)
            except:
                await interaction.response.send_message("No pude encontrar al usuario en el servidor.", ephemeral=True)
                return

            if usuario.id == interaction.user.id:
                await interaction.response.send_message("No puedes expulsarte a ti mismo.", ephemeral=True)
                return

            if usuario.id == self.bot.user.id:
                await interaction.response.send_message("No me puedes expulsar.", ephemeral=True)
                return

            bot_member = interaction.guild.me
            if not interaction.guild.me.guild_permissions.kick_members:
                await interaction.response.send_message("No tengo permisos para expulsar usuarios.", ephemeral=True)
                return

            if usuario.top_role >= bot_member.top_role:
                await interaction.response.send_message("No puedo expulsar a este usuario. Mi rol debe estar por encima del suyo.", ephemeral=True)
                return

            if usuario.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
                await interaction.response.send_message("No puedes expulsar a alguien con un rol igual o superior al tuyo.", ephemeral=True)
                return

            kick_reason = razon if razon else f"Expulsado por {interaction.user.name}"

            await interaction.response.defer()

            try:
                embed = discord.Embed(
                    title="⚠️ Has sido Expulsado",
                    color=discord.Color.orange()
                )
                embed.add_field(name="Servidor:", value=interaction.guild.name, inline=False)
                embed.add_field(name="Moderador:", value=interaction.user.name, inline=False)
                embed.add_field(name="Razón:", value=kick_reason, inline=False)
                embed.timestamp = discord.utils.utcnow()
                
                await usuario.send(embed=embed)
            except:
                pass

            await usuario.kick(reason=kick_reason)
            
            confirmation = discord.Embed(
                title="✅ Usuario Expulsado",
                color=discord.Color.orange()
            )
            confirmation.add_field(name="Usuario:", value=f"{usuario.name} ({usuario.id})", inline=False)
            confirmation.add_field(name="Moderador:", value=f"{interaction.user.name} ({interaction.user.id})", inline=False)
            confirmation.add_field(name="Razón:", value=kick_reason, inline=False)
            confirmation.timestamp = discord.utils.utcnow()

            await interaction.followup.send(embed=confirmation)

            await send_kick_log(
                self.bot,
                guild=interaction.guild,
                target=usuario,
                moderator=interaction.user,
                reason=kick_reason,
                source="command"
            )
        
        except discord.NotFound:
            await interaction.followup.send("No se encontró ningún usuario con esa ID.")
        except discord.Forbidden:
            await interaction.followup.send("No tengo permisos para expulsar a ese usuario.")
        except discord.HTTPException as e:
            await interaction.followup.send(f"Ocurrió un error al intentar expulsar al usuario: {e}")

async def setup(bot):
    await bot.add_cog(Kick(bot))