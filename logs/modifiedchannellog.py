import discord
from discord.ext import commands
from database.get import get_specific_field
from logs.log_utils import LogParser

class ModifiedChannelLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_parser = LogParser(bot)
        self.channel_cache = {}

    def format_permissions_diff(self, before, after):
        try:
            perms_diff = ""
            
            all_targets = set(before.overwrites.keys()) | set(after.overwrites.keys())
            
            for target in all_targets:
                target_name = target.name if hasattr(target, 'name') else str(target)
                
                before_overwrite = before.overwrites_for(target)
                after_overwrite = after.overwrites_for(target)
                
                has_changes = False
                changes_text = ""
                
                for perm, value in after_overwrite:
                    before_value = getattr(before_overwrite, perm)
                    
                    if before_value != value and (before_value is not None or value is not None):
                        has_changes = True
                        perm_name = perm.replace('_', ' ').capitalize()
                        
                        if value is None:
                            changes_text += f"- {perm_name}: Personalizado -> Neutral\n"
                        elif before_value is None:
                            status = "✔️" if value else "❌"
                            changes_text += f"- {perm_name}: Neutral -> {status}\n"
                        else:
                            before_status = "✔️" if before_value else "❌"
                            after_status = "✔️" if value else "❌"
                            changes_text += f"- {perm_name}: {before_status} -> {after_status}\n"
                
                if has_changes:
                    perms_diff += f"Cambios para `@{target_name}`:\n"
                    perms_diff += changes_text
                    perms_diff += "\n"
            
            if not perms_diff:
                perms_diff = "No hubo cambios en los permisos."
                
            if len(perms_diff) > 900:
                perms_diff = perms_diff[:900] + "..."
                
            return perms_diff
        except Exception as e:
            print(f"Error al formatear diferencias de permisos: {e}")
            return "Error al obtener los cambios de permisos."

    async def log_channel_update_event(self, before, after):
        try:
            if not after.guild:
                return
                
            guild_data = get_specific_field(after.guild.id, "audit_logs")
            if not guild_data or "mod_ch" not in guild_data:
                return
            
            mod_channel_config = guild_data["mod_ch"]
            
            is_activated = mod_channel_config.get("activated")
            if isinstance(is_activated, str):
                is_activated = is_activated.lower() == "true"
            
            if not is_activated:
                return
                
            log_channel_id = mod_channel_config.get("log_channel")
            if not log_channel_id or log_channel_id == 0:
                return
            
            log_channel = self.bot.get_channel(int(log_channel_id))
            if not log_channel:
                return
            
            name_changed = before.name != after.name
            perms_changed = before.overwrites != after.overwrites
            
            track_name = mod_channel_config.get("changedname", False)
            track_perms = mod_channel_config.get("changedperms", False)
            
            if not ((track_name and name_changed) or (track_perms and perms_changed)):
                return
            
            message_data = mod_channel_config.get("message", {})
            message_format = mod_channel_config.get("mod_ch_messages", "")
            
            replacements = {}
            
            if message_data and isinstance(message_data, dict):
                await self.log_parser.parse_and_send_log(
                    log_type="mod_ch",
                    log_channel=log_channel,
                    message_format=message_data,
                    channel=after,
                    guild=after.guild,
                    **replacements
                )
            elif message_format:
                await self.log_parser.parse_and_send_log(
                    log_type="mod_ch",
                    log_channel=log_channel,
                    message_format=message_format,
                    channel=after,
                    guild=after.guild,
                    **replacements
                )
            else:
                embed = discord.Embed(
                    title="Canal Modificado",
                    description=f"**Canal:** {after.mention} ({after.id})",
                    color=discord.Color.blue(),
                    timestamp=discord.utils.utcnow()
                )
                
                if track_name and name_changed:
                    embed.add_field(
                        name="Actualización del nombre",
                        value=f"#{before.name} -> #{after.name}",
                        inline=False
                    )
                
                if track_perms and perms_changed:
                    perms_diff = self.format_permissions_diff(before, after)
                    embed.add_field(
                        name="Cambios en permisos",
                        value=perms_diff,
                        inline=False
                    )
                
                await log_channel.send(embed=embed)

        except Exception as e:
            print(f"Error en log_channel_update_event: {e}")

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        if isinstance(after, (discord.TextChannel, discord.VoiceChannel)):
            await self.log_channel_update_event(before, after)

async def setup(bot):
    await bot.add_cog(ModifiedChannelLogs(bot))