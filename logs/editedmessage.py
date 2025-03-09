import discord
from discord.ext import commands
from database.get import get_specific_field
from datetime import datetime, timedelta
import pytz

class EditedMessages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.max_embed_length = 4096
        self.max_message_length = 2000

    def chunk_message(self, message: str, chunk_size: int) -> list:
        return [message[i:i + chunk_size] for i in range(0, len(message), chunk_size)]

    def replace_variables(self, text: str, before: str, after: str, message: discord.Message) -> str:
        replacements = {
            "{user}": message.author.mention,
            "{userid}": str(message.author.id),
            "{usertag}": str(message.author),
            "{channel}": message.channel.mention,
            "{channelid}": str(message.channel.id),
            "{old_msg}": before,
            "{new_msg}": after
        }
        
        result = text
        for key, value in replacements.items():
            result = result.replace(key, str(value))
        return result

    async def log_edited_message(self, before: discord.Message, after: discord.Message):
        try:
            if before.author.bot or before.embeds or after.embeds:
                return

            if not before.content or not after.content:
                return

            if before.content == after.content:
                return

            guild_data = get_specific_field(before.guild.id, "audit_logs")
            if not guild_data or "edited_msg" not in guild_data:
                return
            
            edit_msg_config = guild_data["edited_msg"]
            
            is_activated = edit_msg_config.get("activated")
            if isinstance(is_activated, str):
                is_activated = is_activated.lower() == "true"
            if not is_activated:
                return
                
            log_channel_id = edit_msg_config.get("log_channel")
            if not log_channel_id or log_channel_id == 0:
                return
            
            log_channel = self.bot.get_channel(int(log_channel_id))
            if not log_channel:
                return
            
            ago_days = edit_msg_config.get("ago", 30)
            if not isinstance(ago_days, (int, float)):
                ago_days = 30
                
            current_time = datetime.now(pytz.UTC)
            message_time = before.created_at.replace(tzinfo=pytz.UTC)
            message_age = current_time - message_time
            
            if message_age > timedelta(days=ago_days):
                return
            
            message_format = edit_msg_config.get("edited_msg_messages", "")
            if not message_format:
                return

            if message_format.startswith("embed:"):
                await self.send_embed_log(message_format, before.content, after.content, before, log_channel)
            else:
                await self.send_normal_log(message_format, before.content, after.content, before, log_channel)

        except Exception as e:
            print(f"Error en log_edited_message: {e}")

    async def send_embed_log(self, message_format: str, before: str, after: str, message: discord.Message, log_channel: discord.TextChannel):
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

            description = self.replace_variables(embed_data.get("description", ""), before, after, message)
            chunks = self.chunk_message(description, self.max_embed_length)
            
            for i, chunk in enumerate(chunks):
                embed = discord.Embed(color=discord.Color.blue())
                
                if i == 0 and "title" in embed_data:
                    title = self.replace_variables(embed_data["title"], before, after, message)
                    embed.title = title

                embed.description = chunk

                if i == len(chunks) - 1 and "footer" in embed_data:
                    footer = self.replace_variables(embed_data["footer"], before, after, message)
                    embed.set_footer(text=footer)

                if i > 0:
                    embed.title = f"Continuación ({i+1}/{len(chunks)})"

                embed.timestamp = discord.utils.utcnow()
                await log_channel.send(embed=embed)

        except Exception as e:
            print(f"Error enviando el log embed: {e}")

    async def send_normal_log(self, message_format: str, before: str, after: str, message: discord.Message, log_channel: discord.TextChannel):
        try:
            content = self.replace_variables(message_format, before, after, message)
            
            chunks = self.chunk_message(content, self.max_message_length)
            
            for i, chunk in enumerate(chunks):
                if i > 0:
                    await log_channel.send(f"Continuación ({i+1}/{len(chunks)}):\n{chunk}")
                else:
                    await log_channel.send(chunk)

        except Exception as e:
            print(f"Error enviando log normal: {e}")

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if not before.guild:
            return
        await self.log_edited_message(before, after)

async def setup(bot):
    await bot.add_cog(EditedMessages(bot))