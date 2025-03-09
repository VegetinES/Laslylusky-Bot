import discord
from discord.ext import commands
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

    @commands.command(name="kick")
    async def kick(self, ctx, member: discord.Member = None, *, reason: str = None):
        try:
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

async def setup(bot):
    await bot.add_cog(Kick(bot))