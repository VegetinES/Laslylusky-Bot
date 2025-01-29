import discord
from discord.ext import commands
import random
import requests

class Meme(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="meme")
    async def meme(self, ctx):

        if ctx.channel.type == discord.ChannelType.private:
            return

        url = "https://api.imgflip.com/get_memes"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            memes = data['data']['memes']
            
            meme = random.choice(memes)

            embed = discord.Embed(
                title="Meme Aleatorio",
                description=f"¡Aquí tienes un meme aleatorio! 😊",
                color=discord.Color.random()
            )
            embed.set_image(url=meme['url'])
            embed.set_footer(text=f"Pedido por: {ctx.author.display_name}", icon_url=ctx.author.avatar_url)

            await ctx.send(embed=embed)
        else:
            await ctx.send("No pude obtener un meme en este momento. Intenta más tarde.")

async def setup(bot):
    await bot.add_cog(Meme(bot))