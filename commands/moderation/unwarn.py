import discord
from discord.ext import commands
from discord import app_commands
import time
from database.oracle import Oracle
from database.get import get_specific_field

class Unwarn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Oracle()
    
    @commands.command(name="unwarn", help="Elimina una advertencia de un usuario por su ID")
    @commands.has_permissions(manage_messages=True)
    async def unwarn(self, ctx, warn_id: int, *, reason: str = "Sin razón especificada"):
        try:
            act_commands = get_specific_field(ctx.guild.id, "act_cmd")
            if act_commands is None:
                embed = discord.Embed(
                    title="<:No:825734196256440340> Error de Configuración",
                    description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return

            if "unwarn" not in act_commands:
                await ctx.send("El comando no está activado en este servidor.")
                return

            self.db.connect()

            guild_id = str(ctx.guild.id)
            mod_id = str(ctx.author.id)

            result = self.db.get(guild_id, warn_id=warn_id)
            
            if "error" in result:
                await ctx.send(f"<:No:825734196256440340> Error: {result['error']}")
                self.db.close()
                return

            user_id = result.get("user_id")
            warn_info = result.get("warn")
            
            if not user_id or not warn_info:
                await ctx.send("<:No:825734196256440340> Error: No se pudo recuperar la información de la advertencia.")
                self.db.close()
                return

            unwarn_result = self.db.update(guild_id, user_id, "unwarn", warn_id=warn_id, mod_id=mod_id)
            
            if "error" in unwarn_result:
                await ctx.send(f"<:No:825734196256440340> Error: {unwarn_result['error']}")
                self.db.close()
                return

            try:
                user = await self.bot.fetch_user(int(user_id))
                user_mention = user.mention
                user_tag = str(user)
            except:
                user_mention = f"Usuario (ID: {user_id})"
                user_tag = f"Usuario#{user_id}"

            embed = discord.Embed(
                title="✅ Advertencia eliminada",
                description=f"Se ha eliminado la advertencia con ID **{warn_id}** de {user_mention}",
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow()
            )
            
            embed.add_field(name="Motivo original", value=warn_info.get("razón", "No especificado"), inline=False)
            embed.add_field(name="Motivo de eliminación", value=reason, inline=False)
            embed.add_field(name="Moderador", value=ctx.author.mention, inline=True)
            embed.add_field(name="Fecha", value=f"<t:{int(time.time())}:F>", inline=True)
            
            embed.set_footer(text=f"ID: {warn_id}")
            
            await ctx.send(embed=embed)

            self.bot.dispatch("unwarn", 
                ctx.guild.id, 
                user_id, 
                user_mention, 
                user_tag, 
                reason, 
                mod_id, 
                ctx.author.mention, 
                str(ctx.author),
                warn_id
            )
            
        except Exception as e:
            await ctx.send(f"<:No:825734196256440340> Error al procesar el comando: {str(e)}")
        finally:
            self.db.close()
    
    @app_commands.command(name="unwarn", description="Elimina una advertencia de un usuario por su ID")
    @app_commands.describe(
        warn_id="ID de la advertencia a eliminar",
        reason="Razón por la que se elimina la advertencia"
    )
    @app_commands.default_permissions(manage_messages=True)
    async def slash_unwarn(self, interaction: discord.Interaction, warn_id: int, reason: str):
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

            if "unwarn" not in act_commands:
                await interaction.response.send_message("El comando no está activado en este servidor.", ephemeral=True)
                return
            
            self.db.connect()
            
            guild_id = str(interaction.guild.id)
            mod_id = str(interaction.user.id)
            
            result = self.db.get(guild_id, warn_id=warn_id)
            
            if "error" in result:
                await interaction.response.send_message(f"<:No:825734196256440340> Error: {result['error']}", ephemeral=True)
                self.db.close()
                return
            
            user_id = result.get("user_id")
            warn_info = result.get("warn")
            
            if not user_id or not warn_info:
                await interaction.response.send_message("<:No:825734196256440340> Error: No se pudo recuperar la información de la advertencia.", ephemeral=True)
                self.db.close()
                return
            
            unwarn_result = self.db.update(guild_id, user_id, "unwarn", warn_id=warn_id, mod_id=mod_id)
            
            if "error" in unwarn_result:
                await interaction.response.send_message(f"<:No:825734196256440340> Error: {unwarn_result['error']}", ephemeral=True)
                self.db.close()
                return
            
            try:
                user = await self.bot.fetch_user(int(user_id))
                user_mention = user.mention
                user_tag = str(user)
            except:
                user_mention = f"Usuario (ID: {user_id})"
                user_tag = f"Usuario#{user_id}"
            
            embed = discord.Embed(
                title="✅ Advertencia eliminada",
                description=f"Se ha eliminado la advertencia con ID **{warn_id}** de {user_mention}",
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow()
            )
            
            embed.add_field(name="Motivo original", value=warn_info.get("razón", "No especificado"), inline=False)
            embed.add_field(name="Motivo de eliminación", value=reason, inline=False)
            embed.add_field(name="Moderador", value=interaction.user.mention, inline=True)
            embed.add_field(name="Fecha", value=f"<t:{int(time.time())}:F>", inline=True)
            
            embed.set_footer(text=f"ID: {warn_id}")
            
            await interaction.response.send_message(embed=embed)

            self.bot.dispatch("unwarn", 
                interaction.guild.id, 
                user_id, 
                user_mention, 
                user_tag, 
                reason, 
                mod_id, 
                interaction.user.mention, 
                str(interaction.user),
                warn_id
            )
            
        except Exception as e:
            await interaction.response.send_message(f"<:No:825734196256440340> Error al procesar el comando: {str(e)}", ephemeral=True) # ❌
        finally:
            self.db.close()

async def setup(bot):
    await bot.add_cog(Unwarn(bot))