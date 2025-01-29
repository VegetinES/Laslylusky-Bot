import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timedelta
from yt_dlp import YoutubeDL
from discord import FFmpegPCMAudio
import os
import sys

class Play(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.music_queue = {}
        self.currently_playing = {}
        self.last_activity = {}
        self.voice_clients = {}
        self.pause_time = {}

        self.YDL_OPTIONS = {
            'format': 'bestaudio/best', 
            'nooverwrites': True,
            'no_color': True,
            'no_warnings': True,
            'ignoreerrors': False,
            'no_playlist': True,
            'default_search': 'ytsearch',
            'cookiefile': 'cookies.txt',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        }
        
        ffmpeg_executable = 'ffmpeg.exe' if sys.platform == "win32" else 'ffmpeg'
        self.FFMPEG_OPTIONS = {
            'executable': os.path.join(os.getcwd(), 'ffmpeg_bin', ffmpeg_executable),
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn -filter:a loudnorm'
        }

        self.bot.loop.create_task(self.check_inactivity())

    @commands.command(name="play")
    async def play(self, ctx, *, query):
        if not ctx.author.voice:
            await ctx.send("Debes estar en un canal de voz para usar este comando.")
            return

        channel = ctx.author.voice.channel

        try:
            if ctx.guild.id not in self.voice_clients:
                self.voice_clients[ctx.guild.id] = await channel.connect()

            with YoutubeDL(self.YDL_OPTIONS) as ydl:
                try:
                    info = ydl.extract_info(query, download=False)
                    
                    if 'entries' in info:
                        videos = info['entries']
                    else:
                        videos = [info]

                    for video in videos:
                        song_info = {
                            'name': video['title'],
                            'url': video['webpage_url'],
                            'duration': video.get('duration', 0)
                        }
                        self.music_queue.setdefault(ctx.guild.id, []).append(song_info)

                    self.last_activity[ctx.guild.id] = datetime.now()

                    if not self.currently_playing.get(ctx.guild.id):
                        await self.play_next(ctx)

                    if len(videos) == 1:
                        await ctx.send(f"Añadido a la cola: **{videos[0]['title']}**")
                    else:
                        await ctx.send(f"Añadidos {len(videos)} vídeos a la cola.")
                    
                except Exception as e:
                    await ctx.send(f"Error al buscar el vídeo: {str(e)}")
            
        except Exception as e:
            await ctx.send(f"Error al unirse al canal de voz: {str(e)}")

    async def play_next(self, ctx):
        if not self.music_queue.get(ctx.guild.id):
            self.currently_playing[ctx.guild.id] = None
            return

        song = self.music_queue[ctx.guild.id].pop(0)
        self.currently_playing[ctx.guild.id] = song

        def after_playing(error):
            if error:
                print(f'Player error: {error}')
            asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop)

        try:
            with YoutubeDL(self.YDL_OPTIONS) as ydl:
                info = ydl.extract_info(song['url'], download=False)
                audio_url = info['url']

            source = FFmpegPCMAudio(audio_url, **self.FFMPEG_OPTIONS)
            vc = self.voice_clients[ctx.guild.id]
            vc.play(source, after=after_playing)

            duration = song.get('duration', 'Desconocida')
            await ctx.send(f"Reproduciendo: **{song['name']}** (Duración: {duration} seg)")

        except Exception as e:
            await ctx.send(f"Error al reproducir: {str(e)}")
            self.currently_playing[ctx.guild.id] = None

    async def check_inactivity(self):
        while True:
            await asyncio.sleep(60)
            for guild_id in list(self.voice_clients.keys()):
                if guild_id not in self.last_activity:
                    continue

                vc = self.voice_clients[guild_id]
                if not vc:
                    continue

                if vc.channel and not [m for m in vc.channel.members if not m.bot]:
                    if (datetime.now() - self.last_activity[guild_id]) > timedelta(minutes=10):
                        await self.cleanup(guild_id)
                        continue

                if guild_id in self.pause_time:
                    if (datetime.now() - self.pause_time[guild_id]) > timedelta(minutes=45):
                        await self.cleanup(guild_id)
                        continue

                if not self.currently_playing.get(guild_id) and not self.music_queue.get(guild_id):
                    if (datetime.now() - self.last_activity[guild_id]) > timedelta(minutes=10):
                        await self.cleanup(guild_id)

    async def cleanup(self, guild_id):
        if guild_id in self.voice_clients:
            await self.voice_clients[guild_id].disconnect()
            del self.voice_clients[guild_id]
        self.music_queue[guild_id] = []
        self.currently_playing[guild_id] = None
        if guild_id in self.pause_time:
            del self.pause_time[guild_id]

    @play.error
    async def play_error(self, ctx, error):
        await ctx.send(f"Error: {str(error)}")

async def setup(bot):
    await bot.add_cog(Play(bot))