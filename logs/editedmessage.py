import discord
from discord.ext import commands
from database.get import get_specific_field
from datetime import datetime, timedelta
import pytz
import aiohttp
import base64
import os

class EditedMessages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.max_embed_length = 4096
        self.max_message_length = 2000
        self.max_direct_message_length = 1000
        self.pastebin_api_key = os.getenv("PASTEBIN_API_KEY")
        self.pastebin_user_key = os.getenv("PASTEBIN_USER_KEY")

    def chunk_message(self, message: str, chunk_size: int) -> list:
        return [message[i:i + chunk_size] for i in range(0, len(message), chunk_size)]

    async def create_paste(self, content, title):
        try:
            if not self.pastebin_api_key:
                return None

            data = {
                'api_dev_key': self.pastebin_api_key,
                'api_option': 'paste',
                'api_paste_code': content,
                'api_paste_name': title,
                'api_paste_private': '1',
                'api_paste_expire_date': '1W'
            }
            
            if self.pastebin_user_key:
                data['api_user_key'] = self.pastebin_user_key

            async with aiohttp.ClientSession() as session:
                async with session.post('https://pastebin.com/api/api_post.php', data=data) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        error_text = await response.text()
                        print(f"Error de Pastebin: {error_text}")
                        return None
        except Exception as e:
            print(f"Error al crear paste: {e}")
            return None

    def replace_variables(self, text: str, before: str, after: str, message: discord.Message, before_url=None, after_url=None) -> str:
        replacements = {
            "{user}": message.author.mention,
            "{userid}": str(message.author.id),
            "{usertag}": str(message.author),
            "{channel}": message.channel.mention,
            "{channelid}": str(message.channel.id),
        }
        
        if before_url:
            replacements["{old_msg}"] = f"Texto largo, se ha subido a pastebin [click aquí]({before_url})"
        else:
            replacements["{old_msg}"] = before
            
        if after_url:
            replacements["{new_msg}"] = f"Texto largo, se ha subido a pastebin [click aquí]({after_url})"
        else:
            replacements["{new_msg}"] = after
        
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

            before_content = before.content
            after_content = after.content
            before_url = None
            after_url = None
            
            if len(before_content) > self.max_direct_message_length:
                before_url = await self.create_paste(
                    before_content, 
                    f"Mensaje original - {before.author} - {before.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
                )
                
            if len(after_content) > self.max_direct_message_length:
                after_url = await self.create_paste(
                    after_content, 
                    f"Mensaje editado - {after.author} - {after.edited_at.strftime('%Y-%m-%d %H:%M:%S')}"
                )

            if message_format.startswith("embed:"):
                await self.send_embed_log(message_format, before_content, after_content, before, after, log_channel, before_url, after_url)
            else:
                await self.send_normal_log(message_format, before_content, after_content, before, after, log_channel, before_url, after_url)

        except Exception as e:
            print(f"Error en log_edited_message: {e}")

    async def send_embed_log(self, message_format: str, before: str, after: str, before_message: discord.Message, after_message: discord.Message, log_channel: discord.TextChannel, before_url=None, after_url=None):
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

            description = self.replace_variables(embed_data.get("description", ""), before, after, before_message, before_url, after_url)
            
            embed = discord.Embed(color=discord.Color.blue())
            
            if "title" in embed_data:
                title = self.replace_variables(embed_data["title"], before, after, before_message, before_url, after_url)
                embed.title = title

            embed.description = description

            if "footer" in embed_data:
                footer = self.replace_variables(embed_data["footer"], before, after, before_message, before_url, after_url)
                embed.set_footer(text=footer)

            embed.timestamp = discord.utils.utcnow()
            
            view = discord.ui.View()
            view.add_item(discord.ui.Button(
                label="Mensaje",
                url=after_message.jump_url, 
                style=discord.ButtonStyle.link
            ))
            
            await log_channel.send(embed=embed, view=view)

        except Exception as e:
            print(f"Error enviando el log embed: {e}")

    async def send_normal_log(self, message_format: str, before: str, after: str, before_message: discord.Message, after_message: discord.Message, log_channel: discord.TextChannel, before_url=None, after_url=None):
        try:
            content = self.replace_variables(message_format, before, after, before_message, before_url, after_url)
            
            view = discord.ui.View()
            view.add_item(discord.ui.Button(
                label="Mensaje",
                url=after_message.jump_url, 
                style=discord.ButtonStyle.link
            ))
            
            await log_channel.send(content, view=view)

        except Exception as e:
            print(f"Error enviando log normal: {e}")

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if not before.guild:
            return
        await self.log_edited_message(before, after)

async def setup(bot):
    await bot.add_cog(EditedMessages(bot))