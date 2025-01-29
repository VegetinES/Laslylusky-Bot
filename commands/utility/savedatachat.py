import discord
from discord.ext import commands
import json
from pathlib import Path
import io

class SaveDataChat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.storage_path = Path('data/conversations.json')

    @commands.command(name="savedatachat")
    async def save_data_chat(self, ctx):
        try:
            if not self.storage_path.exists():
                await ctx.reply("No hay datos de conversación disponibles.")
                return
            
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                all_conversations = json.load(f)

            user_id = str(ctx.author.id)
            
            if user_id not in all_conversations:
                await ctx.reply("No tienes ninguna conversación guardada.")
                return
            
            user_data = {
                user_id: all_conversations[user_id]
            }

            json_data = json.dumps(user_data, ensure_ascii=False, indent=2)
            file = discord.File(
                io.StringIO(json_data),
                filename=f'chat_history_{ctx.author.name}.json'
            )

            await ctx.reply("Aquí están tus datos de conversación:", file=file)

        except Exception as e:
            print(f"Error al guardar datos: {e}")
            await ctx.reply("¡Ups! Ocurrió un error al procesar tu solicitud.")

async def setup(bot):
    await bot.add_cog(SaveDataChat(bot))