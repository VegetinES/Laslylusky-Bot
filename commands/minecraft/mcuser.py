from database.get import get_specific_field
import discord
from discord.ext import commands
import aiohttp

class MinecraftProfile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="mcuser")
    async def profile(self, ctx, name: str):
        act_commands = get_specific_field(ctx.guild.id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if "mcuser" not in act_commands:
            await ctx.reply("El comando no está activado en este servidor.")
            return
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://api.mojang.com/users/profiles/minecraft/{name}") as resp:
                    if resp.status != 200:
                        raise Exception("No se encontró el UUID")
                    player_data = await resp.json()
                    uuid = player_data.get("id")
                    
                async with session.get(f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}") as resp:
                    if resp.status != 200:
                        raise Exception("No se encontró datos de la Skin")
                    skin_data = await resp.json()
                    textures = skin_data["properties"][0]["value"]
                    
                body_image_url = f"https://api.mineatar.io/body/full/{uuid}"

            embed = discord.Embed(
                title="Minecraft Player",
                url="https://spectex.xyz/",
                description="**Aquí está la información del jugador solicitado**",
                color=0x31d533
            )
            embed.add_field(name="**Nombre del jugador**", value=f"```{name}```", inline=False)
            embed.add_field(name="**UUID**", value=f"```{uuid}```", inline=False)
            embed.add_field(name="**Texturas**", value=f"[Ver Skin](https://crafatar.com/skins/{uuid})\n[Ver Capa](https://crafatar.com/capes/{uuid})", inline=False)
            embed.set_thumbnail(url=body_image_url)
            embed.set_footer(text="Utilidades de Minecraft")

            await ctx.send(embed=embed)
        except Exception as error:
            embed = discord.Embed(
                title="Utilidades de Minecraft",
                description="**Ha habido un error**",
                color=0xa92626
            )
            embed.add_field(name="Detalles del error", value=f"```{error}```", inline=False)
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(MinecraftProfile(bot))