import discord
from discord.ext import commands
from database.get import get_specific_field
from logs.log_utils import LogParser

class EditedMessages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_parser = LogParser(bot)

    async def log_edited_message(self, before: discord.Message, after: discord.Message):
        try:
            if before.author.bot:
                return

            if before.embeds or after.embeds:
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

            before_content = before.content or "No hay contenido en el mensaje anterior"
            after_content = after.content or "No hay contenido en el mensaje actual"
            before_url = None
            after_url = None

            if len(before_content) > self.log_parser.max_direct_message_length:
                before_url = await self.log_parser.create_paste(
                    before_content, 
                    f"Mensaje original - {before.author} - {before.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
                )
                
            if len(after_content) > self.log_parser.max_direct_message_length:
                after_url = await self.log_parser.create_paste(
                    after_content, 
                    f"Mensaje editado - {after.author} - {after.edited_at.strftime('%Y-%m-%d %H:%M:%S')}"
                )

            message_data = edit_msg_config.get("message", {})
            message_format = edit_msg_config.get("edited_msg_messages", "")
            
            if message_data and isinstance(message_data, dict):
                await self.log_parser.parse_and_send_log(
                    log_type="edited_msg",
                    log_channel=log_channel,
                    message_format=message_data,
                    message=after,
                    old_content=before_content,
                    new_content=after_content,
                    old_url=before_url,
                    new_url=after_url,
                    after_message=after,
                    guild=after.guild
                )
            elif message_format:
                await self.log_parser.parse_and_send_log(
                    log_type="edited_msg",
                    log_channel=log_channel,
                    message_format=message_format,
                    message=after,
                    old_content=before_content,
                    new_content=after_content,
                    old_url=before_url,
                    new_url=after_url,
                    after_message=after,
                    guild=after.guild
                )
            else:
                embed = discord.Embed(
                    title="Mensaje Editado",
                    description=(
                        f"**Autor:** {after.author.mention} ({after.author.id})\n"
                        f"**Canal:** {after.channel.mention} ({after.channel.id})\n\n"
                    ),
                    color=discord.Color.blue(),
                    timestamp=discord.utils.utcnow()
                )
                
                if before_url:
                    embed.add_field(
                        name="Contenido Original",
                        value=f"[Ver mensaje original]({before_url})",
                        inline=False
                    )
                else:
                    embed.add_field(
                        name="Contenido Original",
                        value=before_content,
                        inline=False
                    )
                    
                if after_url:
                    embed.add_field(
                        name="Contenido Nuevo",
                        value=f"[Ver mensaje nuevo]({after_url})",
                        inline=False
                    )
                else:
                    embed.add_field(
                        name="Contenido Nuevo",
                        value=after_content,
                        inline=False
                    )
                
                if after.attachments:
                    attachments_text = self.log_parser.format_attachments(after.attachments)
                    embed.add_field(name="Archivos adjuntos", value=attachments_text, inline=False)
                
                view = discord.ui.View()
                view.add_item(discord.ui.Button(
                    label="Ir al mensaje",
                    url=after.jump_url,
                    style=discord.ButtonStyle.link
                ))
                
                await log_channel.send(embed=embed, view=view)

        except Exception as e:
            print(f"Error en log_edited_message: {e}")

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if not before.guild:
            return
        await self.log_edited_message(before, after)

async def setup(bot):
    await bot.add_cog(EditedMessages(bot))