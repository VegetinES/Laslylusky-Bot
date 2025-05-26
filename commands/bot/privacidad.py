import discord
from discord.ext import commands
from discord import app_commands

class Privacidad(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def create_privacy_embed(self, interaction_or_ctx):
        if isinstance(interaction_or_ctx, discord.Interaction):
            user = interaction_or_ctx.user
        else:
            user = interaction_or_ctx.author

        embed = discord.Embed(
            title="Privacidad al utilizar el bot",
            description=f"Hola <@{user.id}>, aquí hay información sobre nuestra Política de privacidad que debe leer si está interesado en nuestro bot. \n\nA partir de ahora la información sobre la privacidad se encuentra en la [página web](https://laslylusky.es/privacidad)",
            color=discord.Color.random()
        )
        
        embed.set_thumbnail(
            url="https://i.imgur.com/if0NO2o.png"
        )
        
        return embed

    @commands.command(name="privacidad")
    async def privacidad_command(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            return
            
        embed = self.create_privacy_embed(ctx)
        await ctx.send(embed=embed)

    @app_commands.command(
        name="privacidad",
        description="Muestra la política de privacidad del bot"
    )
    async def privacidad_slash(self, interaction: discord.Interaction):
        if isinstance(interaction.channel, discord.DMChannel):
            await interaction.response.send_message(
                "No puedo ejecutar comandos en mensajes directos.",
                ephemeral=True
            )
            return
            
        embed = self.create_privacy_embed(interaction)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Privacidad(bot))