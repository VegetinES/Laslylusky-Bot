from database.get import get_specific_field
import discord
from discord.ext import commands
from api.neko import NekoAPI

class Boobs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="boobs")
    async def boobs(self, ctx):
        if ctx.channel.type == discord.ChannelType.private:
            return
            
        err_message = "<a:Error:830186686624694342> Utiliza este comando en un canal NSFW"
        if not ctx.channel.nsfw:
            await ctx.message.delete()
            return await ctx.reply(err_message, delete_after=3)
        
        act_commands = get_specific_field(ctx.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if "boobs" not in act_commands:
            await ctx.reply("El comando no está activado en este servidor.")
            return
            
        loading_embed = discord.Embed(
            description="Espera por favor...",
            timestamp=discord.utils.utcnow()
        )
        m = await ctx.send(embed=loading_embed)
        
        success, result = await NekoAPI.get_image("boobs")
        
        if success:
            embed_nsfw = discord.Embed(
                description=":underage:\n**[Imagen aquí]({})**".format(result),
                timestamp=discord.utils.utcnow()
            )
            embed_nsfw.set_image(url=result)
            embed_nsfw.set_footer(text="Espera que la imagen cargue")
            await m.edit(embed=embed_nsfw)
        else:
            await m.edit(content=result)

async def setup(bot):
    await bot.add_cog(Boobs(bot))