import discord
from discord.ext import commands
from discord import app_commands

class Suggest(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.max_suggestion_length = 4000

    @commands.command(name="botsuggest")
    async def botsuggest(self, ctx, *, sugerencia: str = None):
        if isinstance(ctx.channel, discord.DMChannel):
            return

        if not sugerencia:
            await ctx.send("Escribe una sugerencia, por favor.")
            return
            
        if len(sugerencia) > self.max_suggestion_length:
            await ctx.send(f"Tu sugerencia excede el límite de {self.max_suggestion_length} caracteres. Por favor, acórtala.")
            return

        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass

        embed_sugerencia = discord.Embed(
            title="Nueva Sugerencia",
            description=f"Sugerencia de {ctx.author.display_name}:\n\n{sugerencia}",
            color=discord.Color.blue(),
            timestamp=ctx.message.created_at
        )
        embed_sugerencia.set_thumbnail(
            url="https://i.imgur.com/if0NO2o.png"
        )
        embed_sugerencia.set_footer(text=f"ID: {ctx.author.id}", icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)

        embed_confirmacion = discord.Embed(
            title="Sugerencia enviada",
            description=(f"Ey {ctx.author.mention}, tu sugerencia ha sido enviada correctamente. "
                         f"Puedes verla en el canal de sugerencias correspondiente."),
            color=discord.Color.blue(),
            timestamp=ctx.message.created_at
        )
        embed_confirmacion.set_thumbnail(
            url="https://i.imgur.com/if0NO2o.png"
        )
        embed_confirmacion.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)

        canal_sugerencias_id = 1343923969811812465
        canal_sugerencias = self.bot.get_channel(canal_sugerencias_id)

        if canal_sugerencias:
            mensaje = await canal_sugerencias.send(embed=embed_sugerencia)
            await mensaje.add_reaction("✅")
            await mensaje.add_reaction("❌")

            try:
                await ctx.author.send(embed=embed_confirmacion)
            except discord.Forbidden:
                await ctx.send(f"{ctx.author.mention}, no pude enviarte un mensaje directo. Aquí tienes la confirmación:",
                               embed=embed_confirmacion)
        else:
            await ctx.send("No se encontró el canal de sugerencias. Avisa a mi administrador y fundador.")

    @app_commands.command(name="botsuggest", description="Envía una sugerencia para el servidor")
    @app_commands.describe(sugerencia="Escribe tu sugerencia aquí")
    async def slash_botsuggest(self, interaction: discord.Interaction, sugerencia: str):
        if isinstance(interaction.channel, discord.DMChannel):
            await interaction.response.send_message("No puedes usar este comando en mensajes directos.", ephemeral=True)
            return
            
        if len(sugerencia) > self.max_suggestion_length:
            await interaction.response.send_message(
                f"Tu sugerencia excede el límite de {self.max_suggestion_length} caracteres. Por favor, acórtala.",
                ephemeral=True
            )
            return

        embed_sugerencia = discord.Embed(
            title="Nueva Sugerencia",
            description=f"Sugerencia de {interaction.user.display_name}:\n\n{sugerencia}",
            color=discord.Color.blue(),
            timestamp=interaction.created_at
        )
        embed_sugerencia.set_thumbnail(
            url="https://i.imgur.com/if0NO2o.png"
        )
        embed_sugerencia.set_footer(text=f"ID: {interaction.user.id}", icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)

        embed_confirmacion = discord.Embed(
            title="Sugerencia enviada",
            description=(f"Ey {interaction.user.mention}, tu sugerencia ha sido enviada correctamente. "
                         f"Puedes verla en el canal de sugerencias correspondiente."),
            color=discord.Color.blue(),
            timestamp=interaction.created_at
        )
        embed_confirmacion.set_thumbnail(
            url="https://i.imgur.com/if0NO2o.png"
        )
        embed_confirmacion.set_footer(text=interaction.user.display_name, icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)

        canal_sugerencias_id = 1343923969811812465
        canal_sugerencias = self.bot.get_channel(canal_sugerencias_id)

        if canal_sugerencias:
            mensaje = await canal_sugerencias.send(embed=embed_sugerencia)
            await mensaje.add_reaction("✅")
            await mensaje.add_reaction("❌")

            await interaction.response.send_message(embed=embed_confirmacion, ephemeral=True)
        else:
            await interaction.response.send_message("No se encontró el canal de sugerencias. Avisa a mi administrador y fundador.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Suggest(bot))