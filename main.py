import discord
from discord.ext import commands
import requests
from dotenv import load_dotenv
import os

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='%', intents = intents)

@bot.command(name='ayuda')
async def ayuda(ctx):
    if isinstance(ctx.channel, discord.DMChannel):
        return

    embed = discord.Embed(
        title="Comandos Laslylusky Bot", 
        description="Comandos actuales\n\nOJO QUE SE VIENEN COSITAS\n\nBot desarrollado por `VegetinES#5088`",
        color=discord.Color.random()
    )
    embed.add_field(name="Comandos Públicos [1]", value="`%ayuda`", inline=False) 
    embed.set_footer(text=f"Pedido por: {ctx.author.display_name}", icon_url=ctx.author.avatar.url)
    
    await ctx.send(embed=embed)

@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.idle,
        activity=discord.Game(name="En mantenimiento, se vienen cosas")
    )
    print(f"Estamos dentro! {bot.user}")

bot.run(os.getenv('DISCORD_TOKEN'))