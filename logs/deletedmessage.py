import discord
from discord.ext import commands
from database.get import get_specific_field
from logs.log_utils import LogParser

class DeletedMessages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_parser = LogParser(bot)

    async def log_deleted_message(self, message: discord.Message):
        try:
            if message.author.bot or message.embeds:
                return

            if not message.content and not message.attachments:
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
            
            message_content = message.content

            if len(message_content) > self.log_parser.max_direct_message_length:
                paste_url = await self.log_parser.create_paste(
                    message_content,
                    f"Mensaje eliminado - {message.author} - {message.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
                )
                if paste_url:
                    del_msg_content = f"Mensaje demasiado largo, ver aquí: {paste_url}"
                else:
                    del_msg_content = message_content[:1000] + "... [mensaje truncado]"
            else:
                del_msg_content = message_content

            message_data = del_msg_config.get("message", {})
            message_format = del_msg_config.get("del_msg_messages", "")

            if message_data and isinstance(message_data, dict):
                await self.log_parser.parse_and_send_log(
                    log_type="del_msg",
                    log_channel=log_channel,
                    message_format=message_data,
                    message=message,
                    author=message.author,
                    del_msg_content=del_msg_content
                )
            elif message_format:
                result = await self.log_parser.create_deleted_message_log(
                    message_format=message_format,
                    message=message,
                    del_msg_content=del_msg_content
                )

                if "embed" in result:
                    await log_channel.send(embed=result["embed"])
                else:
                    await log_channel.send(content=result["content"])
            else:
                embed = discord.Embed(
                    title="Mensaje Eliminado",
                    description=f"**Autor:** {message.author.mention}\n**Canal:** {message.channel.mention}\n\n**Contenido:**\n{del_msg_content}",
                    color=discord.Color.red(),
                    timestamp=discord.utils.utcnow()
                )
                if message.attachments:
                    attachments_text = self.log_parser.format_attachments(message.attachments)
                    embed.add_field(name="Archivos adjuntos", value=attachments_text)
                
                await log_channel.send(embed=embed)

        except Exception as e:
            print(f"Error en log_deleted_message: {e}")

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if not message.guild:
            return
        await self.log_deleted_message(message)

async def setup(bot):
    await bot.add_cog(DeletedMessages(bot))