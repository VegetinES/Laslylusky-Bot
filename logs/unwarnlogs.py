import discord
from discord.ext import commands
from database.get import get_specific_field

class UnwarnLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def log_unwarn_event(self, guild_id, user_id, user_mention, user_tag, reason, mod_id, mod_mention, mod_tag, warn_id):
        try:
            guild_data = get_specific_field(guild_id, "audit_logs")
            if not guild_data or "unwarn" not in guild_data:
                return
            
            unwarn_config = guild_data["unwarn"]
            
            is_activated = unwarn_config.get("activated")
            if isinstance(is_activated, str):
                is_activated = is_activated.lower() == "true"
            
            if not is_activated:
                return
                
            log_channel_id = unwarn_config.get("log_channel")
            if not log_channel_id or log_channel_id == 0:
                return
            
            log_channel = self.bot.get_channel(int(log_channel_id))
            if not log_channel:
                return
            
            message_format = unwarn_config.get("unwarn_messages", "")
            if not message_format:
                return

            message_data = await self.parse_log_message(message_format, user_id, user_mention, user_tag, reason, mod_id, mod_mention, mod_tag, warn_id)
            if message_data:
                if "embed" in message_data:
                    await log_channel.send(embed=message_data["embed"])
                else:
                    await log_channel.send(message_data["content"])

        except Exception as e:
            print(f"Error en log_unwarn_event: {e}")

    def replace_variables(self, text: str, user_id, user_mention, user_tag, reason, mod_id, mod_mention, mod_tag, warn_id) -> str:
        replacements = {
            "{user}": user_mention,
            "{userid}": str(user_id),
            "{usertag}": user_tag,
            "{reason}": reason,
            "{mod}": mod_mention,
            "{modid}": str(mod_id),
            "{modtag}": mod_tag,
            "{warnid}": str(warn_id)
        }
        
        result = text
        for key, value in replacements.items():
            result = result.replace(key, value)
        return result

    async def parse_log_message(self, message: str, user_id, user_mention, user_tag, reason, mod_id, mod_mention, mod_tag, warn_id):
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
                
                embed = discord.Embed(color=discord.Color.green())
                
                if "title" in embed_data:
                    title = self.replace_variables(embed_data["title"], user_id, user_mention, user_tag, reason, mod_id, mod_mention, mod_tag, warn_id)
                    embed.title = title
                if "description" in embed_data:
                    description = self.replace_variables(embed_data["description"], user_id, user_mention, user_tag, reason, mod_id, mod_mention, mod_tag, warn_id)
                    embed.description = description
                if "footer" in embed_data:
                    footer = self.replace_variables(embed_data["footer"], user_id, user_mention, user_tag, reason, mod_id, mod_mention, mod_tag, warn_id)
                    embed.set_footer(text=footer)
                
                embed.timestamp = discord.utils.utcnow()
                
                return {"embed": embed}
            else:
                content = self.replace_variables(message, user_id, user_mention, user_tag, reason, mod_id, mod_mention, mod_tag, warn_id)
                return {"content": content}

        except Exception as e:
            print(f"Error parseando el mensaje del log: {e}")
            return None

    @commands.Cog.listener()
    async def on_unwarn(self, guild_id, user_id, user_mention, user_tag, reason, mod_id, mod_mention, mod_tag, warn_id):
        await self.log_unwarn_event(guild_id, user_id, user_mention, user_tag, reason, mod_id, mod_mention, mod_tag, warn_id)

async def setup(bot):
    await bot.add_cog(UnwarnLogs(bot))