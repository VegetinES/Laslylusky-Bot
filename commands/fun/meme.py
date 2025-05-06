import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import random
from database.get import get_specific_field

class Meme(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.SPANISH_SUBREDDITS = [
            'MemesEnEspanol',
            'SpanishMeme',
            'memesenespanol',
            'MemesESP'
        ]

    @commands.command(name="meme")
    async def meme_text(self, ctx):
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
        
        if "meme" not in act_commands:
            await ctx.reply("El comando no está activado en este servidor.")
            return
            
        async with ctx.typing():
            embed = await self._get_spanish_meme()
            await ctx.send(embed=embed)

    @app_commands.command(name="meme", description="Muestra un meme aleatorio en español")
    async def meme_slash(self, interaction: discord.Interaction):
        act_commands = get_specific_field(interaction.guild_id, "act_cmd")
        if act_commands is None:
            embed = discord.Embed(
                title="<:No:825734196256440340> Error de Configuración",
                description="No hay datos configurados para este servidor. Usa el comando `/config update` si eres administrador para configurar el bot funcione en el servidor",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if "meme" not in act_commands:
            await interaction.response.send_message("El comando no está activado en este servidor.", ephemeral=True)
            return
            
        await interaction.response.defer()
        embed = await self._get_spanish_meme()
        await interaction.followup.send(embed=embed)
    
    async def _get_spanish_meme(self):
        try:
            subreddit = random.choice(self.SPANISH_SUBREDDITS)
            url = f'https://meme-api.com/gimme/{subreddit}'
                
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        for backup_subreddit in self.SPANISH_SUBREDDITS:
                            if backup_subreddit != subreddit:
                                url = f'https://meme-api.com/gimme/{backup_subreddit}'
                                async with session.get(url) as backup_response:
                                    if backup_response.status == 200:
                                        data = await backup_response.json()
                                        break
                        else:
                            return discord.Embed(
                                title="Error",
                                description="😢 No pude obtener memes en español ahora mismo.",
                                color=discord.Color.red()
                            )
                    else:
                        data = await response.json()
                    
                    embed = discord.Embed(
                        title=data.get('title', 'Meme en español'),
                        description=f"De r/{data.get('subreddit', subreddit)} • 👍 {data.get('ups', 0)}",
                        color=discord.Color.red()
                    )
                    embed.set_image(url=data['url'])
                    
                    return embed
                        
        except Exception as e:
            print(f"Error obteniendo meme: {e}")
            return discord.Embed(
                title="Error",
                description="😢 No pude obtener memes en español ahora mismo.",
                color=discord.Color.red()
            )

async def setup(bot):
    await bot.add_cog(Meme(bot))