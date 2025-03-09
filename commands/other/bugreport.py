import discord
from discord.ext import commands
from discord import app_commands

class BugReport(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="bugreport")
    async def bugreport(self, ctx, *, reporte: str = None):
        if isinstance(ctx.channel, discord.DMChannel):
            return

        if not reporte:
            await ctx.send(f"<@{ctx.author.id}>, escribe un mensaje, por favor.\n\n"
                           f"Escribe el comando que funcione mal o que le falta algo y cuál es el problema.")
            return

        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass

        embed_reporte = discord.Embed(
            title="Reporte de Bug",
            description=f"**Reportado por {ctx.author.display_name}:**\n\n{reporte}",
            color=discord.Color.red(),
            timestamp=ctx.message.created_at
        )
        embed_reporte.set_thumbnail(
            url="https://media.discordapp.net/attachments/818410022907412522/824373373185818704/1616616249024.png?width=593&height=593"
        )
        embed_reporte.set_footer(text=f"ID: {ctx.author.id}", icon_url=ctx.author.avatar.url)

        canal_reporte_id = 784768523321999390
        canal_reporte = self.bot.get_channel(canal_reporte_id)

        if canal_reporte:
            await canal_reporte.send(embed=embed_reporte)
            await ctx.send(f"{ctx.author.mention}, tu reporte ha sido enviado correctamente.", ephemeral=True)
        else:
            await ctx.send("No se encontró el canal de reportes. Avisa a mi administrador y fundador.", ephemeral=True)

    @app_commands.command(name="bugreport", description="Reporta un bug del bot")
    @app_commands.describe(
        razonbug="La razón o descripción del bug",
        error="El mensaje de error que mostró el bot (opcional)",
        comando_ejecutado="El comando que causó el error (opcional)"
    )
    async def slash_bugreport(
        self, 
        interaction: discord.Interaction, 
        razonbug: str,
        error: str = None,
        comando_ejecutado: str = None
    ):
        embed_reporte = discord.Embed(
            title="Nuevo reporte",
            description=f"**Descripción:** {razonbug}",
            color=discord.Color.red(),
            timestamp=interaction.created_at
        )
        
        if comando_ejecutado:
            embed_reporte.add_field(
                name="Comando ejecutado",
                value=comando_ejecutado,
                inline=False
            )
            
        if error:
            embed_reporte.add_field(
                name="Mensaje de error del bot",
                value=error,
                inline=False
            )

        embed_reporte.set_thumbnail(
            url="https://media.discordapp.net/attachments/818410022907412522/824373373185818704/1616616249024.png?width=593&height=593"
        )
        embed_reporte.set_footer(text=f"ID: {interaction.user.id}", icon_url=interaction.user.avatar.url)

        canal_reporte_id = 784768523321999390
        canal_reporte = self.bot.get_channel(canal_reporte_id)

        if canal_reporte:
            await canal_reporte.send(embed=embed_reporte)
            await interaction.response.send_message(
                "Tu reporte ha sido enviado correctamente. ¡Gracias por tu colaboración!", 
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "No se encontró el canal de reportes. Avisa a mi administrador y fundador.",
                ephemeral=True
            )

    @commands.command(name="resolvebug")
    async def resolve_bug(self, ctx, mensaje: str):
        if ctx.channel.id != 784768523321999390:
            return

        if ctx.author.id != 702934069138161835:
            return

        try:
            canal = self.bot.get_channel(784768523321999390)
            mensaje_reporte = await canal.fetch_message(int(mensaje))

            if not mensaje_reporte.author.id == self.bot.user.id:
                await ctx.send(
                    "El mensaje especificado no es un reporte de bug válido.", 
                    delete_after=5
                )
                return

            if not mensaje_reporte.embeds:
                await ctx.send(
                    "El mensaje especificado no contiene un reporte de bug.", 
                    delete_after=5
                )
                return

            embed_original = mensaje_reporte.embeds[0]
            embed_nuevo = discord.Embed(
                title="Nuevo reporte (Arreglado)",
                description=embed_original.description,
                color=discord.Color.green(),
                timestamp=embed_original.timestamp
            )

            for field in embed_original.fields:
                embed_nuevo.add_field(
                    name=field.name,
                    value=field.value,
                    inline=field.inline
                )

            if embed_original.thumbnail:
                embed_nuevo.set_thumbnail(url=embed_original.thumbnail.url)
            if embed_original.footer:
                embed_nuevo.set_footer(
                    text=embed_original.footer.text,
                    icon_url=embed_original.footer.icon_url
                )

            await mensaje_reporte.edit(embed=embed_nuevo)
            await ctx.send(
                "El reporte ha sido marcado como resuelto.", 
                delete_after=5
            )
            try:
                await ctx.message.delete()
            except discord.Forbidden:
                pass

        except ValueError:
            await ctx.send(
                "Por favor, proporciona una ID de mensaje válida.", 
                delete_after=5
            )
        except discord.NotFound:
            await ctx.send(
                "No se encontró el mensaje especificado.", 
                delete_after=5
            )
        except discord.Forbidden:
            await ctx.send(
                "No tengo permiso para editar ese mensaje.", 
                delete_after=5
            )
        except Exception as e:
            await ctx.send(
                f"Ocurrió un error al procesar el comando: {str(e)}", 
                delete_after=5
            )

async def setup(bot):
    await bot.add_cog(BugReport(bot))