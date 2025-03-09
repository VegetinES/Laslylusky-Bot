import discord
from discord.ext import commands
from database.get import get_specific_field
from datetime import datetime, timedelta
import pytz

class DeletedMessages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.max_embed_length = 4096

    def chunk_message(self, message: str, chunk_size: int) -> list:
        return [message[i:i + chunk_size] for i in range(0, len(message), chunk_size)]

    def replace_variables(self, text: str, message: discord.Message, author: discord.Member) -> str:
        replacements = {
            "{del_msg}": message.content,
            "{usertag}": str(author),
            "{userid}": str(author.id),
            "{user}": author.mention,
            "{channel}": message.channel.mention,
            "{channelid}": str(message.channel.id)
        }
        
        result = text
        for key, value in replacements.items():
            result = result.replace(key, str(value))
        return result

    async def log_deleted_message(self, message: discord.Message):
        try:
            if message.author.bot or message.embeds:
                return

            if not message.content:
                return

            guild_data = get_specific_field(message.guild.id, "audit_logs")
            if not guild_data or "del_msg" not in guild_data:
                return
            
            del_msg_config = guild_data["del_msg"]
            
            is_activated = del_msg_config.get("activated")
            if isinstance(is_activated, str):
                is_activated = is_activated.lower() == "true"
            if not is_activated:
                return
                
            log_channel_id = del_msg_config.get("log_channel")
            if not log_channel_id or log_channel_id == 0:
                return
            
            log_channel = self.bot.get_channel(int(log_channel_id))
            if not log_channel:
                return
            
            ago_days = del_msg_config.get("ago", 30)
            if not isinstance(ago_days, (int, float)):
                ago_days = 30
                
            current_time = datetime.now(pytz.UTC)
            message_time = message.created_at.replace(tzinfo=pytz.UTC)
            message_age = current_time - message_time
            
            if message_age > timedelta(days=ago_days):
                return
            
            message_format = del_msg_config.get("del_msg_messages", "")
            if not message_format:
                return

            if message_format.startswith("embed:"):
                await self.send_embed_log(message_format, message, log_channel)
            else:
                await self.send_normal_log(message_format, message, log_channel)

        except Exception as e:
            await log_channel.send(f"Error en log_deleted_message: {e}")
            print(f"Error en log_deleted_message: {e}")

    async def send_embed_log(self, message_format: str, message: discord.Message, log_channel: discord.TextChannel):
        try:
            parts = message_format[6:].split(" ")
            embed_data = {}
            current_key = None
            current_value = []
            
            for part in parts:
                if part.startswith("tl:"):
                    if current_key:
                        embed_data[current_key] = " ".join(current_value)
                    current_key = "title"
                    current_value = [part[3:]]
                elif part.startswith("dp:"):
                    if current_key:
                        embed_data[current_key] = " ".join(current_value)
                    current_key = "description"
                    current_value = [part[3:]]
                elif part.startswith("ft:"):
                    if current_key:
                        embed_data[current_key] = " ".join(current_value)
                    current_key = "footer"
                    current_value = [part[3:]]
                else:
                    current_value.append(part)
            
            if current_key:
                embed_data[current_key] = " ".join(current_value)

            base_description = self.replace_variables(embed_data.get("description", ""), message, message.author)
            chunks = self.chunk_message(base_description, self.max_embed_length)
            
            for i, chunk in enumerate(chunks):
                embed = discord.Embed(color=discord.Color.orange())
                
                if i == 0 and "title" in embed_data:
                    title = self.replace_variables(embed_data["title"], message, message.author)
                    embed.title = title

                embed.description = chunk

                if i == len(chunks) - 1 and "footer" in embed_data:
                    footer = self.replace_variables(embed_data["footer"], message, message.author)
                    embed.set_footer(text=footer)

                embed.timestamp = discord.utils.utcnow()
                await log_channel.send(embed=embed)

        except Exception as e:
            await log_channel.send(f"Error al mandar el embed de los logs del mensaje eliminado: {e}")
            print(f"Error al mandar el embed: {e}")

    async def send_normal_log(self, message_format: str, message: discord.Message, log_channel: discord.TextChannel):
        try:
            content = self.replace_variables(message_format, message, message.author)
            
            chunks = self.chunk_message(content, 2000)
            for chunk in chunks:
                await log_channel.send(chunk)

        except Exception as e:
            await log_channel.send(f"Error al mandar el log del mensaje eliminado: {e}")
            print(f"Error al mandar el log: {e}")

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if not message.guild:
            return
        await self.log_deleted_message(message)

async def setup(bot):
    await bot.add_cog(DeletedMessages(bot))