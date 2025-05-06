import random
import discord
from discord.ext import commands
from discord import app_commands
from database.get import get_specific_field

class EightBall(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.responses = [
            'Ciertamente.',
            'Es decididamente así.',
            'Sin duda.',
            'Sí - definitivamente.',
            'Puedes confiar en ello.',
            'Como yo lo veo, sí.',
            'Es lo más probable.',
            'Si.',
            'Las señales dicen que si.',
            'Respuesta confusa, intenta otra vez.',
            'Pregunta de nuevo más tarde.',
            'Mejor no decirte ahora.',
            'No se puede predecir ahora.',
            'Concéntrate y pregunta otra vez.',
            'No cuentes con eso',
            'Mi respuesta es no.',
            'Mis fuentes dicen que no.',
            'Muy dudoso.',
        ]

    @commands.command(name="8ball", aliases=["bola8", "prediccion"])
    async def _8ball_text(self, ctx, *, question=None):
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
        
        if "8ball" not in act_commands:
            await ctx.reply("El comando no está activado en este servidor.")
            return

        if not question:
            await ctx.send("¡Necesitas hacerme una pregunta! Usa `%8ball <pregunta>`")
            return
            
        await self._process_8ball(ctx, question)

    @app_commands.command(name="8ball", description="Consulta la bola mágica 8")
    @app_commands.describe(pregunta="La pregunta que quieres hacerle a la bola mágica")
    async def _8ball_slash(self, interaction: discord.Interaction, pregunta: str):
        act_commands = get_specific_field(interaction.guild_id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if "8ball" not in act_commands:
            await interaction.response.send_message("El comando no está activado en este servidor.", ephemeral=True)
            return
            
        await self._process_8ball(interaction, pregunta)

    async def _process_8ball(self, ctx_or_interaction, question):
        response = random.choice(self.responses)
        
        embed = discord.Embed(color=0x000000)
        embed.set_author(name="🔮 La Bola Mágica ha hablado", icon_url="https://i.imgur.com/siBDyHb.png")
        
        embed.set_thumbnail(url="https://i.imgur.com/siBDyHb.png")
        
        embed.add_field(name="📝 Tu consulta:", value=f"*{question}*", inline=False)
        embed.add_field(name="🎱 Respuesta:", value=f"**{response}**", inline=False)
        
        embed.set_footer(text="El destino está en tus manos...")
        
        if isinstance(ctx_or_interaction, discord.Interaction):
            await ctx_or_interaction.response.send_message(embed=embed)
        else:
            await ctx_or_interaction.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(EightBall(bot))