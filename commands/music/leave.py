import discord
from discord.ext import commands
from singleton import database
import asyncio

class Leave(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}

    @commands.command(name="leave")
    async def leave(self, ctx):
        if not ctx.voice_client:
            await ctx.send("❌ No estoy en un canal de voz.")
            return

        if ctx.voice_client.is_playing():
            channel = ctx.author.voice.channel
            voice_members = len([m for m in channel.members if not m.bot])

            if voice_members > 2:
                msg = await ctx.send("Se requiere votación para sacarme del chat de voz. Reacciona con 👍 para aprobar.")
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
                    await ctx.send("No hay suficientes votos para sacarme.")
                    return

        await ctx.voice_client.disconnect()
        self.queues[ctx.guild.id] = []
        await ctx.send("👋 Me he desconectado del canal de voz.")

async def setup(bot):
    await bot.add_cog(Leave(bot))