import discord
from discord.ext import commands
from singleton import database
import asyncio

class Pause(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="pause")
    async def pause(self, ctx):
        if not ctx.voice_client or not ctx.voice_client.is_playing():
            await ctx.send("❌ No hay música en reproducción")
            return

        channel = ctx.author.voice.channel
        voice_members = len([m for m in channel.members if not m.bot])

        if voice_members > 2:
            msg = await ctx.send(f"Se requiere votación para pausar. Reacciona con 👍 para aprobar")
            await msg.add_reaction("👍")

            def check(reaction, user):
                return (
                    str(reaction.emoji) == "👍"
                    and reaction.message.id == msg.id
                    and not user.bot
                )

            votes_needed = voice_members / 2
            current_votes = 0

            while current_votes < votes_needed:
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
                    current_votes = reaction.count - 1
                except asyncio.TimeoutError:
                    break

            if current_votes < votes_needed:
                await ctx.send("No hay suficientes votos para pausar la música")
                return
            
        ctx.voice_client.pause()
        await ctx.send("⏸ Música pausada")

async def setup(bot):
    await bot.add_cog(Pause(bot))