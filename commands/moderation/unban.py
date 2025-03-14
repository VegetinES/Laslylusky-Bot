import discord
from discord.ext import commands
from discord import app_commands
from database.get import get_specific_field
from logs.unbanlogs import send_unban_log

class Unban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

    @commands.command(name="unban")
    async def unban(self, ctx, user_id: int = None):
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

            if "unban" not in act_commands:
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

            if user_id is None:
                await ctx.reply("Debes proporcionar la ID del usuario a desbanear.")
                return

            try:
                user = await self.bot.fetch_user(user_id)
            except discord.NotFound:
                await ctx.reply("No se encontró ningún usuario con esa ID.")
                return

            try:
                ban_entry = await ctx.guild.fetch_ban(user)
            except discord.NotFound:
                await ctx.reply("Este usuario no está baneado.")
                return
            except discord.Forbidden:
                await ctx.reply("No tengo permisos para ver la lista de baneos.")
                return

            await ctx.guild.unban(user)
            
            embed = discord.Embed(
                title="✅ Usuario Desbaneado",
                color=discord.Color.green()
            )
            embed.add_field(name="Usuario:", value=f"{user} ({user.id})", inline=False)
            embed.add_field(name="Moderador:", value=f"{ctx.author} ({ctx.author.id})", inline=False)
            embed.set_footer(text=f"Desbaneado por: {ctx.author}", icon_url=ctx.author.display_avatar.url)
            embed.timestamp = discord.utils.utcnow()

            await ctx.send(embed=embed)

            await send_unban_log(
                self.bot,
                guild=ctx.guild,
                target=user,
                moderator=ctx.author,
                source="command"
            )

        except discord.Forbidden:
            await ctx.reply("No tengo permisos para desbanear usuarios.")
        except discord.HTTPException as e:
            await ctx.reply(f"Ocurrió un error al intentar desbanear al usuario: {e}")
        except Exception as e:
            await ctx.reply(f"Error al ejecutar el comando: {str(e)}")

    @app_commands.command(name="unban", description="Desbanea a un usuario mediante su ID")
    @app_commands.describe(usuario_id="ID del usuario a desbanear")
    @app_commands.default_permissions(ban_members=True)
    async def slash_unban(self, interaction: discord.Interaction, usuario_id: str):
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

            if "unban" not in act_commands:
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

            try:
                user_id = int(usuario_id)
            except ValueError:
                await interaction.response.send_message("La ID debe ser un número.", ephemeral=True)
                return

            try:
                user = await self.bot.fetch_user(user_id)
            except discord.NotFound:
                await interaction.response.send_message("No se encontró ningún usuario con esa ID.", ephemeral=True)
                return

            await interaction.response.defer()

            try:
                ban_entry = await interaction.guild.fetch_ban(user)
            except discord.NotFound:
                await interaction.followup.send("Este usuario no está baneado.")
                return
            except discord.Forbidden:
                await interaction.followup.send("No tengo permisos para ver la lista de baneos.")
                return

            await interaction.guild.unban(user)
            
            embed = discord.Embed(
                title="✅ Usuario Desbaneado",
                color=discord.Color.green()
            )
            embed.add_field(name="Usuario:", value=f"{user} ({user.id})", inline=False)
            embed.add_field(name="Moderador:", value=f"{interaction.user} ({interaction.user.id})", inline=False)
            embed.set_footer(text=f"Desbaneado por: {interaction.user}", icon_url=interaction.user.display_avatar.url)
            embed.timestamp = discord.utils.utcnow()

            await interaction.followup.send(embed=embed)

            await send_unban_log(
                self.bot,
                guild=interaction.guild,
                target=user,
                moderator=interaction.user,
                source="command"
            )

        except discord.Forbidden:
            await interaction.followup.send("No tengo permisos para desbanear usuarios.")
        except discord.HTTPException as e:
            await interaction.followup.send(f"Ocurrió un error al intentar desbanear al usuario: {e}")
        except Exception as e:
            await interaction.followup.send(f"Error al ejecutar el comando: {str(e)}")

async def setup(bot):
    await bot.add_cog(Unban(bot))