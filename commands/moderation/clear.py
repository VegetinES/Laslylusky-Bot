import discord
from discord.ext import commands
from singleton import database

class ClearMessages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="clear")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int = None):
        if isinstance(ctx.channel, discord.DMChannel):
            return

        if amount is None:
            await ctx.reply('Por favor, indica la cantidad de mensajes que deseas eliminar (ejemplo: `%clear 5`).')
            return

        if amount > 100:
            await ctx.reply('No puedes borrar más de 100 mensajes a la vez.')
            return

        if amount < 1:
            await ctx.reply('Debes borrar al menos 1 mensaje.')
            return

        try:
            await ctx.channel.purge(limit=amount + 1)
            confirmation = await ctx.send(embed=discord.Embed(
                description=f"✅ Se han eliminado {amount} mensajes.",
                color=discord.Color.random()
            ))
            await confirmation.delete(delay=3)
        except discord.Forbidden:
            await ctx.reply('No tengo permisos para borrar mensajes en este canal.')
        except discord.HTTPException as e:
            await ctx.reply(f"Ocurrió un error al intentar borrar mensajes: {e}")

async def setup(bot):
    await bot.add_cog(ClearMessages(bot))