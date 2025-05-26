import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import re
import time
from datetime import timedelta
from database.get import get_specific_field
from logs.banlogs import send_ban_log
from database.oracle import Oracle

class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.time_pattern = re.compile(r'^(\d+)([smd])$')
        self.max_ban_days = 15
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
    
    def parse_time(self, time_str):
        if not time_str:
            return None, None
        
        match = self.time_pattern.match(time_str)
        if not match:
            return None, "Formato de tiempo incorrecto. Usa formato: número+s/m/d. Ejemplo: 1d, 5h, 30m, 10s"
        
        value, unit = match.groups()
        value = int(value)
        
        if unit == 's':
            seconds = value
            time_text = f"{value} segundo{'s' if value != 1 else ''}"
        elif unit == 'm':
            seconds = value * 60
            time_text = f"{value} minuto{'s' if value != 1 else ''}"
        elif unit == 'd':
            seconds = value * 86400
            time_text = f"{value} día{'s' if value != 1 else ''}"
        else:
            return None, "Unidad de tiempo no válida. Usa s (segundos), m (minutos) o d (días)."

        if seconds > self.max_ban_days * 86400:
            return None, f"El tiempo máximo de ban es de {self.max_ban_days} días."
        
        return seconds, time_text

    async def schedule_unban(self, guild, user_id, seconds):
        await asyncio.sleep(seconds)
        try:
            guild = self.bot.get_guild(guild.id)
            if guild:
                try:
                    await guild.unban(discord.Object(id=user_id), reason="Ban temporal finalizado")
                    print(f"Usuario {user_id} desbaneado automáticamente de {guild.name}")

                    try:
                        self.db.connect()
                        self.db.update(str(guild.id), str(user_id), "unban")
                        self.db.close()
                    except Exception as e:
                        print(f"Error al registrar el desbaneo en la base de datos: {e}")
                except Exception as e:
                    print(f"Error al desbanear a {user_id} de {guild.name}: {e}")
        except Exception as e:
            print(f"Error al ejecutar el desbaneo programado: {e}")

    async def get_member_autocomplete(self, interaction: discord.Interaction, current: str):
        members = interaction.guild.members
        results = []
        
        for member in members:
            if current.lower() in member.name.lower() or current.lower() in str(member.id):
                display_name = member.display_name if member.display_name != member.name else ""
                display_text = f"{member.name}"
                if display_name:
                    display_text += f" ({display_name})"
                display_text += f" - ID: {member.id}"
                
                results.append(app_commands.Choice(name=display_text, value=str(member.id)))
                
                if len(results) >= 25:
                    break
                    
        return results

    @commands.command(name="ban")
    async def ban(self, ctx, target: discord.Member = None, *, args=None):
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
        
        if "ban" not in act_commands:
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
            
        if target.id == ctx.author.id:
            await ctx.reply("No puedes banearte a ti mismo.")
            return
            
        if target.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            await ctx.reply("No puedes banear a alguien con un rol igual o superior al tuyo.")
            return

        reason = None
        ban_time = None
        time_text = None
        
        if args:
            words = args.split()
            last_word = words[-1]
            
            seconds, time_result = self.parse_time(last_word)
            if seconds is not None:
                ban_time = seconds
                time_text = time_result
                reason = " ".join(words[:-1]) if len(words) > 1 else None
            else:
                reason = args
        
        ban_reason = reason if reason else f"Baneado por {ctx.author.name}"
        
        reasons = []
        if ban_reason:
            reasons.append(ban_reason)
        if time_text:
            reasons.append(f"Ban temporal: {time_text}")
            
        ban_reason_display = " | ".join(reasons)

        try:
            embed = discord.Embed(
                title="⚠️ Aviso de Baneo",
                color=discord.Color.purple()
            )
            embed.add_field(name="Servidor:", value=ctx.guild.name, inline=False)
            embed.add_field(name="Moderador:", value=ctx.author.name, inline=False)
            embed.add_field(name="Razón:", value=ban_reason_display, inline=False)
            embed.timestamp = discord.utils.utcnow()

            try:
                dm_message = await target.send(embed=embed)
                await dm_message.add_reaction("✅")

                def check(reaction, usr):
                    return usr == target and str(reaction.emoji) == "✅"
                
                try:
                    await self.bot.wait_for("reaction_add", check=check, timeout=30)
                except asyncio.TimeoutError:
                    pass
                    
            except (discord.Forbidden, discord.HTTPException):
                await ctx.reply("No puedo enviarle un mensaje directo, baneándolo de todas formas")

            await ctx.guild.ban(target, reason=ban_reason_display, delete_message_days=0)

            try:
                self.db.connect()
                current_timestamp = int(time.time())
                ban_result = self.db.insert(
                    str(ctx.guild.id),
                    str(target.id),
                    str(ctx.author.id),
                    ban_reason_display,
                    "ban",
                    current_timestamp
                )
                self.db.close()
            except Exception as e:
                print(f"Error al registrar el ban en la base de datos: {e}")
            
            confirmation = discord.Embed(
                title="✅ Usuario Baneado",
                color=discord.Color.red()
            )
            confirmation.add_field(name="Usuario:", value=f"{target.name} ({target.id})", inline=False)
            confirmation.add_field(name="Moderador:", value=f"{ctx.author.name} ({ctx.author.id})", inline=False)
            confirmation.add_field(name="Razón:", value=ban_reason_display, inline=False)
            confirmation.timestamp = discord.utils.utcnow()

            await ctx.send(embed=confirmation)

            await send_ban_log(
                self.bot,
                guild=ctx.guild,
                target=target,
                moderator=ctx.author,
                reason=ban_reason_display,
                source="command"
            )
            
            if ban_time:
                self.bot.loop.create_task(self.schedule_unban(ctx.guild, target.id, ban_time))
        
        except discord.NotFound:
            await ctx.reply("No se encontró al usuario")
        except discord.Forbidden:
            await ctx.reply("No tengo permisos para banear a ese usuario. Asegurate que mi rol esté por encima del rol al que quieres banear o tenga permisos necesarios")
        except discord.HTTPException as e:
            await ctx.reply(f"Ocurrió un error al intentar banear al usuario: {e}")
        except asyncio.TimeoutError:
            await ctx.reply("El usuario no reaccionó a tiempo, no será baneado")

    @app_commands.command(name="ban", description="Banea a un usuario del servidor")
    @app_commands.describe(
        usuario="Usuario a banear",
        tiempo="Tiempo del baneo (s para segundos, m para minutos, d para días. Máximo 15 días). Ejemplo: 1d",
        razon="Razón del baneo",
        eliminar_mensajes="Número de días de mensajes a eliminar (1-7)"
    )
    @app_commands.autocomplete(usuario=get_member_autocomplete)
    @app_commands.choices(eliminar_mensajes=[
        app_commands.Choice(name="No eliminar mensajes", value=0),
        app_commands.Choice(name="1 día de mensajes", value=1),
        app_commands.Choice(name="2 días de mensajes", value=2),
        app_commands.Choice(name="3 días de mensajes", value=3),
        app_commands.Choice(name="4 días de mensajes", value=4),
        app_commands.Choice(name="5 días de mensajes", value=5),
        app_commands.Choice(name="6 días de mensajes", value=6),
        app_commands.Choice(name="7 días de mensajes", value=7)
    ])
    @app_commands.default_permissions(ban_members=True)
    async def slash_ban(self, interaction: discord.Interaction, usuario: str, tiempo: str = None, razon: str = None, eliminar_mensajes: int = 0):
        act_commands = get_specific_field(interaction.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if "ban" not in act_commands:
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
        
        if eliminar_mensajes < 0 or eliminar_mensajes > 7:
            await interaction.response.send_message("El número de días para eliminar mensajes debe estar entre 0 y 7.", ephemeral=True)
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
        
        ban_time = None
        time_text = None
        if tiempo:
            seconds, time_result = self.parse_time(tiempo)
            if seconds is not None:
                ban_time = seconds
                time_text = time_result
            else:
                await interaction.response.send_message(time_result, ephemeral=True)
                return
        
        ban_reason = razon if razon else f"Baneado por {interaction.user.name}"
        
        reasons = []
        if ban_reason:
            reasons.append(ban_reason)
        if time_text:
            reasons.append(f"Ban temporal: {time_text}")
            
        ban_reason_display = " | ".join(reasons)
        
        try:
            embed = discord.Embed(
                title="⚠️ Aviso de Baneo",
                color=discord.Color.purple()
            )
            embed.add_field(name="Servidor:", value=interaction.guild.name, inline=False)
            embed.add_field(name="Moderador:", value=interaction.user.name, inline=False)
            embed.add_field(name="Razón:", value=ban_reason_display, inline=False)
                
            embed.set_footer(text=f"Hecho por: {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
            embed.timestamp = discord.utils.utcnow()
            
            try:
                if isinstance(user_obj, discord.Member):
                    await user_obj.send(embed=embed)
            except (discord.Forbidden, discord.HTTPException):
                pass
            
            await interaction.response.defer()
            
            await interaction.guild.ban(discord.Object(id=user_id), reason=ban_reason_display, delete_message_days=eliminar_mensajes)
            
            try:
                self.db.connect()
                current_timestamp = int(time.time())
                ban_result = self.db.insert(
                    str(interaction.guild.id),
                    str(user_id),
                    str(interaction.user.id),
                    ban_reason_display,
                    "ban",
                    current_timestamp
                )
                self.db.close()
            except Exception as e:
                print(f"Error al registrar el ban en la base de datos: {e}")
            
            confirmation = discord.Embed(
                title="✅ Usuario Baneado",
                color=discord.Color.red()
            )
            confirmation.add_field(name="Usuario:", value=f"{user_obj.name} ({user_obj.id})", inline=False)
            confirmation.add_field(name="Moderador:", value=f"{interaction.user.name} ({interaction.user.id})", inline=False)
            confirmation.add_field(name="Razón:", value=ban_reason_display, inline=False)
                
            confirmation.set_footer(text=f"CreatedBy: {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
            confirmation.timestamp = discord.utils.utcnow()
            
            await interaction.followup.send(embed=confirmation)
            
            await send_ban_log(
                self.bot,
                guild=interaction.guild,
                target=user_obj,
                moderator=interaction.user,
                reason=ban_reason_display,
                source="command"
            )
            
            if ban_time:
                self.bot.loop.create_task(self.schedule_unban(interaction.guild, user_obj.id, ban_time))
            
        except discord.NotFound:
            await interaction.followup.send("No se encontró al usuario")
        except discord.Forbidden:
            await interaction.followup.send("No tengo permisos para banear a ese usuario. Asegurate que mi rol esté por encima del rol al que quieres banear o tenga permisos necesarios")
        except discord.HTTPException as e:
            await interaction.followup.send(f"Ocurrió un error al intentar banear al usuario: {e}")

async def setup(bot):
    await bot.add_cog(Ban(bot))