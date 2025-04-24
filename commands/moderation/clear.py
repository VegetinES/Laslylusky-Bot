import discord
from discord.ext import commands
from discord import app_commands
from database.get import get_specific_field
from typing import Optional

class Clear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def check_custom_permissions(self, ctx):
        perms_data = get_specific_field(ctx.guild.id, "perms")
        if not perms_data:
            return False
        
        if str(ctx.author.id) in perms_data.get("mg-msg-users", []) or str(ctx.author.id) in perms_data.get("admin-users", []):
            return True

        author_role_ids = [str(role.id) for role in ctx.author.roles]
        allowed_msg_roles = perms_data.get("mg-msg-roles", [])
        allowed_admin_roles = perms_data.get("admin-roles", [])
        
        return any(role_id in allowed_msg_roles or role_id in allowed_admin_roles for role_id in author_role_ids)

    async def check_custom_permissions_interaction(self, interaction):
        perms_data = get_specific_field(interaction.guild.id, "perms")
        if not perms_data:
            return False
        
        if str(interaction.user.id) in perms_data.get("mg-msg-users", []) or str(interaction.user.id) in perms_data.get("admin-users", []):
            return True

        author_role_ids = [str(role.id) for role in interaction.user.roles]
        allowed_msg_roles = perms_data.get("mg-msg-roles", [])
        allowed_admin_roles = perms_data.get("admin-roles", [])
        
        return any(role_id in allowed_msg_roles or role_id in allowed_admin_roles for role_id in author_role_ids)

    @commands.command(name="clear")
    async def clear(self, ctx, amount: int = None):
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
        
        if "clear" not in act_commands:
            await ctx.reply("El comando no está activado en este servidor.")
            return

        has_permission = (ctx.author.guild_permissions.manage_messages or 
                         ctx.author.guild_permissions.administrator or 
                         await self.check_custom_permissions(ctx))
        
        if not has_permission:
            await ctx.reply("No tienes permisos para usar este comando.")
            return

        if amount is None:
            await ctx.reply('Por favor, indica la cantidad de mensajes que deseas eliminar (ejemplo: `%clear 5`).')
            return

        if amount < 1:
            await ctx.reply('Debes borrar al menos 1 mensaje.')
            return
            
        if amount > 100:
            amount = 100

        try:
            await ctx.channel.purge(limit=amount + 1)
            confirmation = await ctx.send(embed=discord.Embed(
                description=f"✅ Se han eliminado {amount} mensajes.",
                color=discord.Color.random()
            ))
            await confirmation.delete(delay=3)
        except discord.Forbidden:
            await ctx.reply('No tengo permisos para borrar mensajes en este canal.')
        except discord.HTTPException as e:
            await ctx.reply(f"Ocurrió un error al intentar borrar mensajes: {e}")

    async def channel_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        channels = [
            app_commands.Choice(name=channel.name, value=str(channel.id))
            for channel in interaction.guild.text_channels
            if current.lower() in channel.name.lower()
        ]
        return channels[:25]

    async def user_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        members = []
        for member in interaction.guild.members:
            if current.lower() in member.name.lower() or current.lower() in member.display_name.lower():
                members.append(app_commands.Choice(name=member.display_name, value=str(member.id)))
        return members[:25]

    @app_commands.command(name="clear", description="Elimina un número específico de mensajes")
    @app_commands.describe(
        cantidad="Número de mensajes a eliminar",
        usuario="Usuario cuyos mensajes se eliminarán (opcional)",
        canal="Canal donde se eliminarán los mensajes (opcional)"
    )
    @app_commands.autocomplete(
        usuario=user_autocomplete,
        canal=channel_autocomplete
    )
    @app_commands.default_permissions(manage_messages=True)
    async def slash_clear(
        self, 
        interaction: discord.Interaction, 
        cantidad: int,
        usuario: Optional[str] = None,
        canal: Optional[str] = None
    ):
        act_commands = get_specific_field(interaction.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if "clear" not in act_commands:
            await interaction.response.send_message("El comando no está activado en este servidor.", ephemeral=True)
            return

        has_permission = (interaction.user.guild_permissions.manage_messages or 
                         interaction.user.guild_permissions.administrator or 
                         await self.check_custom_permissions_interaction(interaction))
        
        if not has_permission:
            await interaction.response.send_message("No tienes permisos para usar este comando.", ephemeral=True)
            return

        if cantidad < 1:
            await interaction.response.send_message('Debes borrar al menos 1 mensaje.', ephemeral=True)
            return
            
        if cantidad > 100:
            cantidad = 100

        target_channel = None
        if canal:
            target_channel = interaction.guild.get_channel(int(canal))
            if not target_channel:
                await interaction.response.send_message('No se pudo encontrar el canal especificado.', ephemeral=True)
                return
        else:
            target_channel = interaction.channel

        target_user = None
        if usuario:
            try:
                target_user = await interaction.guild.fetch_member(int(usuario))
                if not target_user:
                    await interaction.response.send_message('No se pudo encontrar el usuario especificado.', ephemeral=True)
                    return
            except:
                await interaction.response.send_message('No se pudo encontrar el usuario especificado.', ephemeral=True)
                return

        await interaction.response.defer(ephemeral=True)
        
        try:
            if target_user:
                def check(message):
                    return message.author.id == target_user.id
                
                deleted = await target_channel.purge(limit=cantidad, check=check)
                
                confirmation = discord.Embed(
                    description=f"✅ Se han eliminado {len(deleted)} mensajes de {target_user.mention} en {target_channel.mention}.",
                    color=discord.Color.random()
                )
            else:
                deleted = await target_channel.purge(limit=cantidad)
                
                confirmation = discord.Embed(
                    description=f"✅ Se han eliminado {len(deleted)} mensajes en {target_channel.mention}.",
                    color=discord.Color.random()
                )
            
            await interaction.followup.send(embed=confirmation, ephemeral=True)
            
        except discord.Forbidden:
            await interaction.followup.send('No tengo permisos para borrar mensajes en ese canal.', ephemeral=True)
        except discord.HTTPException as e:
            await interaction.followup.send(f"Ocurrió un error al intentar borrar mensajes: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Clear(bot))