import discord
from discord.ext import commands
from database.get import get_specific_field

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

    @commands.command(name="clear")
    async def clear(self, ctx, amount: int = None):
        if isinstance(ctx.channel, discord.DMChannel):
            return
            
        act_commands = get_specific_field(ctx.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando </config update:1348248454610161751> si eres administrador para configurar el bot funcione en el servidor",
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

        if amount > 100:
            await ctx.reply('No puedes borrar más de 100 mensajes a la vez.')
            return

        if amount < 1:
            await ctx.reply('Debes borrar al menos 1 mensaje.')
            return

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

async def setup(bot):
    await bot.add_cog(Clear(bot))