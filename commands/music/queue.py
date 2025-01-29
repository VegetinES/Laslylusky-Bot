import discord
from discord.ext import commands

class Queue(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="queue")
    async def queue(self, ctx):
        if not ctx.author.voice:
            await ctx.send("Debes estar en un canal de voz para usar este comando.")
            return
        
        play_cog = self.bot.get_cog("Play")
        if not play_cog:
            await ctx.send("El módulo de reproducción no está cargado.")
            return

        music_queue = play_cog.music_queue

        if ctx.guild.id not in music_queue or not music_queue[ctx.guild.id]:
            await ctx.send("La cola está vacía.")
            return

        queue_list = music_queue[ctx.guild.id]

        embed = discord.Embed(
            title="Cola de canciones",
            color=discord.Color.blue()
        )

        for idx, song in enumerate(queue_list, start=1):
            embed.add_field(
                name=f"{idx}. {song['name']}",
                value=f"Duración: {song.get('duration', 'Desconocida')} segundos\n[YouTube Link]({song['url']})",
                inline=False
            )

        await ctx.send(embed=embed)

async def setup(bot):
    
    await bot.add_cog(Queue(bot))