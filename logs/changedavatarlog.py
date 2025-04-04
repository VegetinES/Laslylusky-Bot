import discord
from discord.ext import commands
from database.get import get_specific_field
from logs.log_utils import LogParser

class ChangedAvatarLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_parser = LogParser(bot)
        self.user_avatar_cache = {}
        self.user_name_cache = {}

    async def log_avatar_name_change_event(self, before, after, guild):
        try:
            if not guild:
                return
                
            guild_data = get_specific_field(guild.id, "audit_logs")
            if not guild_data or "changed_av" not in guild_data:
                return
            
            changed_av_config = guild_data["changed_av"]
            
            is_activated = changed_av_config.get("activated")
            if isinstance(is_activated, str):
                is_activated = is_activated.lower() == "true"
            
            if not is_activated:
                return
                
            log_channel_id = changed_av_config.get("log_channel")
            if not log_channel_id or log_channel_id == 0:
                return
            
            log_channel = self.bot.get_channel(int(log_channel_id))
            if not log_channel:
                return
            
            old_avatar = before.avatar.url if before and hasattr(before, 'avatar') and before.avatar else None
            new_avatar = after.avatar.url if after and hasattr(after, 'avatar') and after.avatar else None
            
            try:
                old_name = str(before) if before else "Unknown"
                new_name = str(after) if after else "Unknown"
            except Exception:
                old_name = before.name if before and hasattr(before, 'name') else "Unknown"
                new_name = after.name if after and hasattr(after, 'name') else "Unknown"
            
            name_changed = old_name != new_name
            avatar_changed = old_avatar != new_avatar
            
            if not name_changed and not avatar_changed:
                return
            
            member = guild.get_member(after.id)
            if not member:
                return
            
            message_data = changed_av_config.get("message", {})
            message_format = changed_av_config.get("changed_av_messages", "")
            
            old_avatar_text = f"[Ver avatar anterior]({old_avatar})" if old_avatar else "Sin avatar"
            new_avatar_text = f"[Ver avatar nuevo]({new_avatar})" if new_avatar else "Sin avatar"
            
            if message_data and isinstance(message_data, dict):
                await self.log_parser.parse_and_send_log(
                    log_type="changed_av",
                    log_channel=log_channel,
                    message_format=message_data,
                    user=member,
                    old_avatar=old_avatar,
                    new_avatar=new_avatar,
                    old_name=old_name if name_changed else None,
                    new_name=new_name if name_changed else None,
                    guild=guild,
                    old_avatar_link=old_avatar_text,
                    new_avatar_link=new_avatar_text
                )
            elif message_format:
                await self.log_parser.parse_and_send_log(
                    log_type="changed_av",
                    log_channel=log_channel,
                    message_format=message_format,
                    user=member,
                    old_avatar=old_avatar,
                    new_avatar=new_avatar,
                    old_name=old_name if name_changed else None,
                    new_name=new_name if name_changed else None,
                    guild=guild,
                    old_avatar_link=old_avatar_text,
                    new_avatar_link=new_avatar_text
                )
            else:
                embed = discord.Embed(
                    title="Cambio de Avatar/Nombre",
                    description=f"**Usuario:** {member.mention} ({member.id})",
                    color=discord.Color.blue(),
                    timestamp=discord.utils.utcnow()
                )
                
                if name_changed:
                    embed.add_field(
                        name="Nombre Anterior",
                        value=old_name,
                        inline=True
                    )
                    embed.add_field(
                        name="Nombre Nuevo",
                        value=new_name,
                        inline=True
                    )
                
                if avatar_changed:
                    embed.add_field(
                        name="Avatar Anterior",
                        value=old_avatar_text,
                        inline=False
                    )
                    
                    if old_avatar:
                        embed.set_thumbnail(url=old_avatar)
                
                    embed.add_field(
                        name="Avatar Nuevo",
                        value=new_avatar_text,
                        inline=False
                    )
                    
                    if new_avatar:
                        embed.set_image(url=new_avatar)
                
                await log_channel.send(embed=embed)

        except Exception as e:
            print(f"Error en log_avatar_name_change_event: {e}")
            import traceback
            traceback.print_exc()

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        try:
            for guild in self.bot.guilds:
                member = guild.get_member(after.id)
                if member:
                    await self.log_avatar_name_change_event(before, after, guild)
        except Exception as e:
            print(f"Error in on_user_update: {e}")
            import traceback
            traceback.print_exc()

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        try:
            if before.nick != after.nick:
                await self.log_avatar_name_change_event(before, after, after.guild)
        except Exception as e:
            print(f"Error in on_member_update: {e}")
            import traceback
            traceback.print_exc()

async def setup(bot):
    await bot.add_cog(ChangedAvatarLogs(bot))