import discord
from discord.ext import commands
from discord import app_commands
import time
from database.get import get_specific_field
from logs.banlogs import send_ban_log
from database.oracle import Oracle

class MassBan(commands.Cog):
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

    @commands.command(name="massban")
    async def prefix_massban(self, ctx, *, args=None):
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
        
        if "massban" not in act_commands:
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

        if not args:
            await ctx.reply("Formato correcto: `%massban ID1 ID2 ID3 ... | Razón del baneo`")
            return
        
        parts = args.split('|', 1)
        
        if len(parts) < 2:
            await ctx.reply("Debes proporcionar una razón para el baneo masivo después del símbolo |")
            return
        
        ids_str = parts[0].strip()
        razon = parts[1].strip()
        
        if not razon:
            await ctx.reply("Debes proporcionar una razón para el baneo masivo.")
            return
        
        user_ids = []
        try:
            for id_str in ids_str.split():
                user_id = int(id_str.strip())
                user_ids.append(user_id)
        except ValueError:
            await ctx.reply("Formato de IDs incorrecto. Proporciona IDs válidas separadas por espacios.")
            return
        
        if not user_ids:
            await ctx.reply("No se proporcionaron IDs válidas.")
            return

        msg = await ctx.send("Procesando baneos masivos...")
        
        banned_users = []
        failed_users = []
        current_timestamp = int(time.time())

        for user_id in user_ids:
            try:
                if user_id == ctx.author.id:
                    failed_users.append((user_id, "No puedes banearte a ti mismo"))
                    continue
                
                if user_id == ctx.guild.owner_id:
                    failed_users.append((user_id, "No puedes banear al propietario del servidor"))
                    continue
                
                try:
                    user = await self.bot.fetch_user(user_id)
                    username = str(user)
                except:
                    user = discord.Object(id=user_id)
                    username = f"Usuario {user_id}"
                    user.name = username
                
                try:
                    await ctx.guild.fetch_ban(discord.Object(id=user_id))
                    failed_users.append((user_id, "El usuario ya está baneado"))
                    continue
                except discord.NotFound:
                    pass
                
                ban_reason = f"{razon} | Baneo masivo por {ctx.author.name}"
                await ctx.guild.ban(discord.Object(id=user_id), reason=ban_reason)
                
                try:
                    self.db.connect()
                    ban_result = self.db.insert(
                        str(ctx.guild.id),
                        str(user_id),
                        str(ctx.author.id),
                        ban_reason,
                        "ban",
                        current_timestamp
                    )
                    self.db.close()
                except Exception as e:
                    print(f"Error al registrar el ban para {user_id} en la base de datos: {e}")
                
                banned_users.append((user_id, username))
                
                await send_ban_log(
                    self.bot,
                    guild=ctx.guild,
                    target=user,
                    moderator=ctx.author,
                    reason=ban_reason,
                    source="command"
                )
                
            except discord.Forbidden:
                failed_users.append((user_id, "Permisos insuficientes"))
            except Exception as e:
                failed_users.append((user_id, f"Error: {str(e)[:100]}"))
        
        embed = discord.Embed(
            title="Resultado del Baneo Masivo",
            color=discord.Color.red() if not banned_users else discord.Color.green()
        )
        
        if banned_users:
            banned_list = "\n".join([f"• {username} (ID: {user_id})" for user_id, username in banned_users])
            embed.add_field(
                name=f"<:Si:825734135116070962> Usuarios baneados correctamente ({len(banned_users)})",
                value=banned_list[:1024] if len(banned_list) <= 1024 else f"{banned_list[:1020]}...",
                inline=False
            )
        
        if failed_users:
            failed_list = "\n".join([f"• ID {user_id}: {reason}" for user_id, reason in failed_users])
            embed.add_field(
                name=f"<:No:825734196256440340> Fallos al banear ({len(failed_users)})",
                value=failed_list[:1024] if len(failed_list) <= 1024 else f"{failed_list[:1020]}...",
                inline=False
            )
        
        embed.add_field(name="Razón del baneo:", value=razon, inline=False)
        embed.set_footer(text=f"Ejecutado por: {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()
        
        await msg.edit(content=None, embed=embed)

    @app_commands.command(name="massban", description="Banea a múltiples usuarios a la vez usando IDs")
    @app_commands.describe(
        ids="IDs de usuarios a banear separadas por espacios",
        razon="Razón del baneo masivo (obligatorio)"
    )
    @app_commands.default_permissions(ban_members=True)
    async def massban(self, interaction: discord.Interaction, ids: str, razon: str):
        act_commands = get_specific_field(interaction.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if "massban" not in act_commands:
            await interaction.response.send_message("El comando de ban no está activado en este servidor.", ephemeral=True)
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
            await interaction.response.send_message("Debes proporcionar una razón para el baneo masivo.", ephemeral=True)
            return
        
        user_ids = []
        try:
            for id_str in ids.split():
                user_id = int(id_str.strip())
                user_ids.append(user_id)
        except ValueError:
            await interaction.response.send_message("Formato de IDs incorrecto. Proporciona IDs válidas separadas por espacios.", ephemeral=True)
            return
        
        if not user_ids:
            await interaction.response.send_message("No se proporcionaron IDs válidas.", ephemeral=True)
            return

        await interaction.response.defer()
        
        banned_users = []
        failed_users = []
        current_timestamp = int(time.time())

        for user_id in user_ids:
            try:
                if user_id == interaction.user.id:
                    failed_users.append((user_id, "No puedes banearte a ti mismo"))
                    continue
                
                if user_id == interaction.guild.owner_id:
                    failed_users.append((user_id, "No puedes banear al propietario del servidor"))
                    continue
                
                try:
                    user = await self.bot.fetch_user(user_id)
                    username = str(user)
                except:
                    user = discord.Object(id=user_id)
                    username = f"Usuario {user_id}"
                    user.name = username
                
                try:
                    await interaction.guild.fetch_ban(discord.Object(id=user_id))
                    failed_users.append((user_id, "El usuario ya está baneado"))
                    continue
                except discord.NotFound:
                    pass
                
                ban_reason = f"{razon} | Baneo masivo por {interaction.user.name}"
                await interaction.guild.ban(discord.Object(id=user_id), reason=ban_reason)

                try:
                    self.db.connect()
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
                    print(f"Error al registrar el ban para {user_id} en la base de datos: {e}")
                
                banned_users.append((user_id, username))
                
                await send_ban_log(
                    self.bot,
                    guild=interaction.guild,
                    target=user,
                    moderator=interaction.user,
                    reason=ban_reason,
                    source="command"
                )
                
            except discord.Forbidden:
                failed_users.append((user_id, "Permisos insuficientes"))
            except Exception as e:
                failed_users.append((user_id, f"Error: {str(e)[:100]}"))
        
        embed = discord.Embed(
            title="Resultado del Baneo Masivo",
            color=discord.Color.red() if not banned_users else discord.Color.green()
        )
        
        if banned_users:
            banned_list = "\n".join([f"• {username} (ID: {user_id})" for user_id, username in banned_users])
            embed.add_field(
                name=f"<:Si:825734135116070962> Usuarios baneados correctamente ({len(banned_users)})",
                value=banned_list[:1024] if len(banned_list) <= 1024 else f"{banned_list[:1020]}...",
                inline=False
            )
        
        if failed_users:
            failed_list = "\n".join([f"• ID {user_id}: {reason}" for user_id, reason in failed_users])
            embed.add_field(
                name=f"<:No:825734196256440340> Fallos al banear ({len(failed_users)})",
                value=failed_list[:1024] if len(failed_list) <= 1024 else f"{failed_list[:1020]}...",
                inline=False
            )
        
        embed.add_field(name="Razón del baneo:", value=razon, inline=False)
        embed.set_footer(text=f"Ejecutado por: {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()
        
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(MassBan(bot))