import discord
from discord.ext import commands
import asyncio
from database.get import get_specific_field
from logs.banlogs import send_ban_log

class Ban(commands.Cog):
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

    @commands.command(name="ban")
    async def ban(self, ctx, target: discord.Member = None, *, reason: str = None):
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

        if target is None:
            await ctx.reply("Menciona al usuario, usa su ID o su nombre de usuario.")
            return
            
        if target.id == ctx.author.id:
            await ctx.reply("No puedes banearte a ti mismo.")
            return
            
        if target.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            await ctx.reply("No puedes banear a alguien con un rol igual o superior al tuyo.")
            return

        ban_reason = reason if reason else f"Baneado por {ctx.author.name}"

        try:
            embed = discord.Embed(
                title="⚠️ Aviso de Baneo",
                color=discord.Color.purple()
            )
            embed.add_field(name="Servidor:", value=ctx.guild.name, inline=False)
            embed.add_field(name="Moderador:", value=ctx.author.name, inline=False)
            embed.add_field(name="Razón:", value=ban_reason, inline=False)
            embed.set_footer(text=f"Hecho por: {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
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

            await ctx.guild.ban(target, reason=ban_reason, delete_message_days=0)
            
            confirmation = discord.Embed(
                title="✅ Usuario Baneado",
                color=discord.Color.red()
            )
            confirmation.add_field(name="Usuario:", value=f"{target.name} ({target.id})", inline=False)
            confirmation.add_field(name="Moderador:", value=f"{ctx.author.name} ({ctx.author.id})", inline=False)
            confirmation.add_field(name="Razón:", value=ban_reason, inline=False)
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
        except asyncio.TimeoutError:
            await ctx.reply("El usuario no reaccionó a tiempo, no será baneado")

async def setup(bot):
    await bot.add_cog(Ban(bot))