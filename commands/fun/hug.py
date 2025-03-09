from database.get import get_specific_field
import discord
import aiohttp
from discord.ext import commands
from commands.configuration.configdata import check_command

class HugCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="hug")
    async def hug(self, ctx, member: discord.Member = None):
        act_commands = get_specific_field(ctx.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando </config update:1348248454610161751> si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if "hug" not in act_commands:
            await ctx.reply("El comando no está activado en este servidor.")
            return
        
        if member is None:
            return await ctx.reply("Uso correcto: `%hug @usuario`", mention_author=False)
        
        url = "https://some-random-api.com/animu/hug"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    if response.status != 200:
                        return await ctx.reply("¡Ocurrió un error al obtener la imagen!", mention_author=False)
                    data = await response.json()
                    gif_url = data["link"]
            except Exception as e:
                return await ctx.reply("¡Ocurrió un error inesperado!", mention_author=False)
        
        embed = discord.Embed(title=f"{ctx.author.display_name} abraza a {member.display_name}")
        embed.set_image(url=gif_url)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(HugCommand(bot))