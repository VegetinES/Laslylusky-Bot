import discord
from discord.ext import commands
from discord import app_commands

class Tos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def create_tos_embed(self, interaction_or_ctx):
        if isinstance(interaction_or_ctx, discord.Interaction):
            user = interaction_or_ctx.user
        else:
            user = interaction_or_ctx.author

        embed = discord.Embed(
            title="Términos de Servicio del Bot",
            description=f"Hola <@{user.id}>, puedes consultar la ToS en la [página web](https://laslylusky.es/tos)",
            color=discord.Color.random()
        )
        
        embed.set_thumbnail(
            url="https://i.imgur.com/if0NO2o.png"
        )
        
        return embed

    @commands.command(name="tos")
    async def tos_command(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            return
            
        embed = self.create_tos_embed(ctx)
        await ctx.send(embed=embed)

    @app_commands.command(
        name="tos",
        description="Muestra los términos de servicio del bot"
    )
    async def tos_slash(self, interaction: discord.Interaction):
        if isinstance(interaction.channel, discord.DMChannel):
            await interaction.response.send_message(
                "No puedo ejecutar comandos en mensajes directos.",
                ephemeral=True
            )
            return
            
        embed = self.create_tos_embed(interaction)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Tos(bot))