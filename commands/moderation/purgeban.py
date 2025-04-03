import discord
from discord.ext import commands
from discord import app_commands
import time
from database.get import get_specific_field
from logs.banlogs import send_ban_log
from database.oracle import Oracle

class PurgeBan(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Oracle()
    
    async def check_custom_permissions(self, ctx):
        perms_data = get_specific_field(ctx.guild.id, "perms")
        if not perms_data:
            return False
        
        if str(ctx.author.id) in perms_data.get("ban-users", []) or str(ctx.author.id) in perms_data.get("admin-users", []):
            return True

        author_role_ids = [str(role.id) for role in ctx.author.roles]
        allowed_msg_roles = perms_data.get("ban-roles", [])
        allowed_admin_roles = perms_data.get("admin-roles", [])
        
        return any(role_id in allowed_msg_roles or role_id in allowed_admin_roles for role_id in author_role_ids)
    
    async def check_custom_permissions_interaction(self, interaction):
        perms_data = get_specific_field(interaction.guild.id, "perms")
        if not perms_data:
            return False
        
        if str(interaction.user.id) in perms_data.get("ban-users", []) or str(interaction.user.id) in perms_data.get("admin-users", []):
            return True

        author_role_ids = [str(role.id) for role in interaction.user.roles]
        allowed_msg_roles = perms_data.get("ban-roles", [])
        allowed_admin_roles = perms_data.get("admin-roles", [])
        
        return any(role_id in allowed_msg_roles or role_id in allowed_admin_roles for role_id in author_role_ids)

    async def get_member_autocomplete(self, interaction: discord.Interaction, current: str):
        members = interaction.guild.members
        return [
            app_commands.Choice(name=f"{member.name}#{member.discriminator if member.discriminator != '0' else ''} ({member.id})", value=str(member.id))
            for member in members if current.lower() in member.name.lower() or current.lower() in str(member.id)
        ][:25]
    
    @commands.command(name="purgeban")
    async def purgeban(self, ctx, target: discord.Member = None, *, reason = None):
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
        
        if "purgeban" not in act_commands:
            await ctx.reply("El comando no está activado en este servidor.")
            return

        has_permission = (ctx.author.guild_permissions.ban_members or 
                         ctx.author.guild_permissions.administrator or 
                         await self.check_custom_permissions(ctx))
        
        if not has_permission:
            embed = discord.Embed(
                title="**No tienes permiso para usar este comando**",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if not ctx.guild.me.guild_permissions.ban_members:
            await ctx.reply("No tengo permisos para banear usuarios en este servidor.")
            return

        if target is None:
            await ctx.reply("Menciona al usuario, usa su ID o su nombre de usuario.")
            return
            
        if reason is None:
            await ctx.reply("Debes proporcionar una razón para el baneo con purga de mensajes.")
            return
            
        if target.id == ctx.author.id:
            await ctx.reply("No puedes banearte a ti mismo.")
            return
            
        if target.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            await ctx.reply("No puedes banear a alguien con un rol igual o superior al tuyo.")
            return

        ban_reason = f"{reason} | PurgeBan por {ctx.author.name}"

        try:
            embed = discord.Embed(
                title="⚠️ Aviso de Baneo con Purga",
                color=discord.Color.purple()
            )
            embed.add_field(name="Servidor:", value=ctx.guild.name, inline=False)
            embed.add_field(name="Moderador:", value=ctx.author.name, inline=False)
            embed.add_field(name="Razón:", value=ban_reason, inline=False)
            embed.add_field(name="Nota:", value="Todos tus mensajes serán eliminados", inline=False)
            embed.set_footer(text=f"Hecho por: {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
            embed.timestamp = discord.utils.utcnow()

            try:
                await target.send(embed=embed)  
            except (discord.Forbidden, discord.HTTPException):
                await ctx.reply("No puedo enviarle un mensaje directo, baneándolo de todas formas")
            
            await ctx.guild.ban(target, reason=ban_reason, delete_message_days=7)

            try:
                self.db.connect()
                current_timestamp = int(time.time())
                ban_result = self.db.insert(
                    str(ctx.guild.id),
                    str(target.id),
                    str(ctx.author.id),
                    ban_reason,
                    "ban",
                    current_timestamp
                )
                self.db.close()
            except Exception as e:
                print(f"Error al registrar el purgeban en la base de datos: {e}")
            
            confirmation = discord.Embed(
                title="<:Si:825734135116070962> Usuario Baneado con Purga",
                color=discord.Color.red()
            )
            confirmation.add_field(name="Usuario:", value=f"{target.name} ({target.id})", inline=False)
            confirmation.add_field(name="Moderador:", value=f"{ctx.author.name} ({ctx.author.id})", inline=False)
            confirmation.add_field(name="Razón:", value=ban_reason, inline=False)
            confirmation.add_field(name="Mensajes:", value="Se han eliminado los mensajes de los últimos 7 días", inline=False)
            confirmation.set_footer(text=f"CreatedBy: {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
            confirmation.timestamp = discord.utils.utcnow()

            await ctx.send(embed=confirmation)

            await send_ban_log(
                self.bot,
                guild=ctx.guild,
                target=target,
                moderator=ctx.author,
                reason=ban_reason,
                source="command"
            )
        
        except discord.NotFound:
            await ctx.reply("No se encontró al usuario")
        except discord.Forbidden:
            await ctx.reply("No tengo permisos para banear a ese usuario. Asegurate que mi rol esté por encima del rol al que quieres banear o tenga permisos necesarios")
        except discord.HTTPException as e:
            await ctx.reply(f"Ocurrió un error al intentar banear al usuario: {e}")

    @app_commands.command(name="purgeban", description="Banea a un usuario eliminando todos sus mensajes")
    @app_commands.describe(
        usuario="Usuario a banear",
        razon="Razón del baneo (obligatorio)"
    )
    @app_commands.autocomplete(usuario=get_member_autocomplete)
    @app_commands.default_permissions(ban_members=True)
    async def slash_purgeban(self, interaction: discord.Interaction, usuario: str, razon: str):
        act_commands = get_specific_field(interaction.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if "purgeban" not in act_commands:
            await interaction.response.send_message("El comando no está activado en este servidor.", ephemeral=True)
            return
        
        has_permission = (interaction.user.guild_permissions.ban_members or 
                         interaction.user.guild_permissions.administrator or 
                         await self.check_custom_permissions_interaction(interaction))
        
        if not has_permission:
            embed = discord.Embed(
                title="**No tienes permiso para usar este comando**",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if not interaction.guild.me.guild_permissions.ban_members:
            await interaction.response.send_message("No tengo permisos para banear usuarios en este servidor.", ephemeral=True)
            return
        
        if not razon:
            await interaction.response.send_message("Debes proporcionar una razón para el baneo con purga.", ephemeral=True)
            return
            
        try:
            user_id = int(usuario)
            try:
                member = await interaction.guild.fetch_member(user_id)
            except discord.NotFound:
                try:
                    user_obj = await self.bot.fetch_user(user_id)
                except:
                    await interaction.response.send_message("No se pudo encontrar un usuario con esa ID.", ephemeral=True)
                    return
            else:
                user_obj = member
        except ValueError:
            await interaction.response.send_message("ID de usuario inválida.", ephemeral=True)
            return
        
        if user_obj.id == interaction.user.id:
            await interaction.response.send_message("No puedes banearte a ti mismo.", ephemeral=True)
            return

        if isinstance(user_obj, discord.Member):
            if user_obj.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
                await interaction.response.send_message("No puedes banear a alguien con un rol igual o superior al tuyo.", ephemeral=True)
                return
        
        ban_reason = f"{razon} | PurgeBan por {interaction.user.name}"
        
        try:
            embed = discord.Embed(
                title="⚠️ Aviso de Baneo con Purga",
                color=discord.Color.purple()
            )
            embed.add_field(name="Servidor:", value=interaction.guild.name, inline=False)
            embed.add_field(name="Moderador:", value=interaction.user.name, inline=False)
            embed.add_field(name="Razón:", value=ban_reason, inline=False)
            embed.add_field(name="Nota:", value="Todos tus mensajes serán eliminados", inline=False)
            embed.set_footer(text=f"Hecho por: {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
            embed.timestamp = discord.utils.utcnow()
            
            try:
                if isinstance(user_obj, discord.Member):
                    await user_obj.send(embed=embed)
            except (discord.Forbidden, discord.HTTPException):
                pass
            
            await interaction.response.defer()

            await interaction.guild.ban(discord.Object(id=user_id), reason=ban_reason, delete_message_days=7)
            
            try:
                self.db.connect()
                current_timestamp = int(time.time())
                ban_result = self.db.insert(
                    str(interaction.guild.id),
                    str(user_id),
                    str(interaction.user.id),
                    ban_reason,
                    "ban",
                    current_timestamp
                )
                self.db.close()
            except Exception as e:
                print(f"Error al registrar el purgeban en la base de datos: {e}")
            
            confirmation = discord.Embed(
                title="<:Si:825734135116070962> Usuario Baneado con Purga",
                color=discord.Color.red()
            )
            confirmation.add_field(name="Usuario:", value=f"{user_obj.name} ({user_obj.id})", inline=False)
            confirmation.add_field(name="Moderador:", value=f"{interaction.user.name} ({interaction.user.id})", inline=False)
            confirmation.add_field(name="Razón:", value=ban_reason, inline=False)
            confirmation.add_field(name="Mensajes:", value="Se han eliminado los mensajes de los últimos 7 días", inline=False)
            confirmation.set_footer(text=f"CreatedBy: {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
            confirmation.timestamp = discord.utils.utcnow()
            
            await interaction.followup.send(embed=confirmation)
            
            await send_ban_log(
                self.bot,
                guild=interaction.guild,
                target=user_obj,
                moderator=interaction.user,
                reason=ban_reason,
                source="command"
            )
            
        except discord.NotFound:
            await interaction.followup.send("No se encontró al usuario")
        except discord.Forbidden:
            await interaction.followup.send("No tengo permisos para banear a ese usuario. Asegurate que mi rol esté por encima del rol al que quieres banear o tenga permisos necesarios")
        except discord.HTTPException as e:
            await interaction.followup.send(f"Ocurrió un error al intentar banear al usuario: {e}")

async def setup(bot):
    await bot.add_cog(PurgeBan(bot))