import discord
from discord.ext import commands
import time

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping")
    async def ping_command(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            return
        
        ping_message = await ctx.send("Aquí tienes mi latencia...")

        latency = ping_message.created_at.timestamp() - ctx.message.created_at.timestamp()
        api_latency = round(self.bot.latency * 1000)

        embed = discord.Embed(
            title="Ping",
            color=discord.Color.from_rgb(17, 190, 211),
            timestamp=ctx.message.created_at
        )
        embed.add_field(name="Mi latencia es:", value=f"{latency * 1000:.2f}ms", inline=True)
        embed.add_field(name="La latencia de mi API es:", value=f"{api_latency}ms", inline=True)
        embed.add_field(name="Llevo encendido:", value=self.format_uptime(), inline=True)
        embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/784774864766500864/2cef87cccba0f00826a16740ac049231.webp")
        embed.set_footer(
            text="Ping",
            icon_url="https://cdn.discordapp.com/avatars/784774864766500864/2cef87cccba0f00826a16740ac049231.webp"
        )

        await ctx.send(embed=embed)

    def format_uptime(self):
        uptime_seconds = time.time() - self.bot.start_time
        uptime_string = time.strftime("%H:%M:%S", time.gmtime(uptime_seconds))
        return uptime_string

async def setup(bot):
    if not hasattr(bot, 'start_time'):
        bot.start_time = time.time()
    await bot.add_cog(Ping(bot))
