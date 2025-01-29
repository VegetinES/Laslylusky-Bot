import discord
from discord.ext import commands
import asyncio

class Skip(commands.Cog):
    def __init__(self, bot, music_queue, currently_playing, voice_clients):
        self.bot = bot
        self.music_queue = music_queue
        self.currently_playing = currently_playing
        self.voice_clients = voice_clients
        self.skip_votes = {}

    @commands.command(name="skip")
    async def skip(self, ctx):
        if not ctx.author.voice:
            await ctx.send("❌ Debes estar en un canal de voz para usar este comando.")
            return

        if ctx.guild.id not in self.voice_clients or not self.voice_clients[ctx.guild.id].is_playing():
            await ctx.send("❌ No hay ninguna canción reproduciéndose actualmente.")
            return

        channel = ctx.author.voice.channel
        voice_members = len([m for m in channel.members if not m.bot])

        if voice_members > 2:
            if ctx.guild.id not in self.skip_votes:
                self.skip_votes[ctx.guild.id] = set()

            if ctx.author.id not in self.skip_votes[ctx.guild.id]:
                self.skip_votes[ctx.guild.id].add(ctx.author.id)
                votes_needed = (voice_members // 2) + 1
                current_votes = len(self.skip_votes[ctx.guild.id])

                await ctx.send(f"🗳️ Voto para saltar registrado. ({current_votes}/{votes_needed})")

                if current_votes >= votes_needed:
                    await self.skip_song(ctx.guild.id, ctx)
                    del self.skip_votes[ctx.guild.id]
                else:
                    await ctx.send("🎵 Aún no hay suficientes votos para saltar la canción.")
            else:
                await ctx.send("⚠️ Ya has votado para saltar esta canción.")
        else:
            await self.skip_song(ctx.guild.id, ctx)

    async def skip_song(self, guild_id, ctx):
        vc = self.voice_clients[guild_id]
        if vc and vc.is_playing():
            vc.stop()

        if guild_id in self.music_queue and self.music_queue[guild_id]:
            await ctx.send("⏭️ Saltando canción...")
            self.currently_playing[guild_id] = None
            self.bot.loop.create_task(self.bot.get_cog("Play").play_next(ctx))
        else:
            await ctx.send("🎶 No hay más canciones en la cola para reproducir.")
            self.currently_playing[guild_id] = None

    @skip.error
    async def skip_error(self, ctx, error):
        await ctx.send(f"❌ Error: {str(error)}")

async def setup(bot):
    play_cog = bot.get_cog("Play")
    if play_cog:
        await bot.add_cog(Skip(bot, play_cog.music_queue, play_cog.currently_playing, play_cog.voice_clients))