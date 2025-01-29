import discord
from discord.ext import commands
import requests

class Anal(commands.Cog): 
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="anal") 
    async def anal(self, ctx): 
        if ctx.channel.type == discord.ChannelType.private:
            return

        err_message = "<a:Error:830186686624694342> Utiliza este comando en un canal NSFW"
        if not ctx.channel.nsfw:
            await ctx.message.delete()
            return await ctx.reply(err_message, delete_after=3)

        loading_embed = discord.Embed(
            description="Espera por favor...", 
            timestamp=discord.utils.utcnow()
        )
        m = await ctx.send(embed=loading_embed)

        try:
            url = "https://nekobot.xyz/api/image"
            params = {"type": "anal"}

            response = requests.get(url, params=params)
            response.raise_for_status()

            image_url = response.json()['message']
            embed_nsfw = discord.Embed(
                description=":underage:\n**[Imagen aquí]({})**".format(image_url),
                timestamp=discord.utils.utcnow()
            )
            embed_nsfw.set_image(url=image_url)
            embed_nsfw.set_footer(text="Espera que la imagen cargue")

            await m.edit(embed=embed_nsfw)

        except requests.exceptions.RequestException as e:
            await m.edit(content="Hubo un error al obtener la imagen.")
            print(f"Error en la solicitud: {e}")

async def setup(bot):
    await bot.add_cog(Anal(bot))