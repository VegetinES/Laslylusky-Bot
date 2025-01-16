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
            description=f"Hola <@{user.id}>, aquí hay información sobre nuestra Política de privacidad que debe leer si está interesado en nuestro bot.",
            color=discord.Color.random()
        )
        
        embed.set_thumbnail(
            url="https://media.discordapp.net/attachments/772803956379222016/1329014967239839744/2cef87cccba0f00826a16740ac049231.png?ex=6788cd24&is=67877ba4&hm=72e8520e7b4654280d6cadf0ac23cec37de06f70eaaa647cc6a87883401569c0&=&format=webp&quality=lossless3"
        )
        
        embed.add_field(
            name="¿Qué datos almacenamos?",
            value="Actualmente ninguno"
        )
        
        embed.add_field(
            name="¿Quién tiene acceso a esos datos?",
            value="El único usuario que tiene acceso a esos datos es el fundador `VegetinES (vegetines)`"
        )
        
        embed.add_field(
            name="¿Para qué se utilizan esos datos?",
            value="Esos datos se guardan solo para hacer estadísticas de la actividad del bot y también para hacer que el bot sea más fácil de utilizar por todos los usuarios"
        )
        
        embed.add_field(
            name="Dudas",
            value="Si tienes alguna duda, entra en el servidor de Discord oficial del bot (escribe `%discord`)"
        )
        
        embed.set_footer(
            text=f"Pedido por: {user.display_name}",
            icon_url=user.avatar.url
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
    try:
        synced = await bot.tree.sync()
        print(f"Sincronizados {len(synced)} comandos de barra")
    except Exception as e:
        print(f"Error sincronizando comandos de barra: {e}")