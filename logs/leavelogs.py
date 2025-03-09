import discord
from discord.ext import commands
from database.get import get_specific_field

class LeaveLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def log_leave_event(self, member: discord.Member):
        try:
            guild_data = get_specific_field(member.guild.id, "audit_logs")
            if not guild_data or "leave" not in guild_data:
                return
            
            leave_config = guild_data["leave"]
            
            is_activated = leave_config.get("activated")
            if isinstance(is_activated, str):
                is_activated = is_activated.lower() == "true"
            
            if not is_activated:
                return
                
            log_channel_id = leave_config.get("log_channel")
            if not log_channel_id or log_channel_id == 0:
                return
            
            log_channel = self.bot.get_channel(int(log_channel_id))
            if not log_channel:
                return
            
            message_format = leave_config.get("leave_messages", "")
            if not message_format:
                return

            message_data = await self.parse_log_message(message_format, member)
            if message_data:
                if "embed" in message_data:
                    await log_channel.send(embed=message_data["embed"])
                else:
                    await log_channel.send(message_data["content"])

        except Exception as e:
            print(f"Error en log_leave_event: {e}")

    def replace_variables(self, text: str, member: discord.Member) -> str:
        replacements = {
            "{usertag}": str(member),
            "{userid}": str(member.id)
        }
        
        result = text
        for key, value in replacements.items():
            result = result.replace(key, value)
        return result

    async def parse_log_message(self, message: str, member: discord.Member):
        try:
            if message.startswith("embed:"):
                parts = message[6:].split(" ")
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
                
                embed = discord.Embed(color=discord.Color.red())
                
                if "title" in embed_data:
                    title = self.replace_variables(embed_data["title"], member)
                    embed.title = title
                if "description" in embed_data:
                    description = self.replace_variables(embed_data["description"], member)
                    embed.description = description
                if "footer" in embed_data:
                    footer = self.replace_variables(embed_data["footer"], member)
                    embed.set_footer(text=footer)
                
                embed.timestamp = discord.utils.utcnow()
                
                return {"embed": embed}
            else:
                content = self.replace_variables(message, member)
                return {"content": content}

        except Exception as e:
            print(f"Error parseando el log del mensaje: {e}")
            return None

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        await self.log_leave_event(member)

async def setup(bot):
    await bot.add_cog(LeaveLogs(bot))