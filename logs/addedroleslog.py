import discord
from discord.ext import commands
from database.get import get_specific_field
from logs.log_utils import LogParser

class AddedRolesLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_parser = LogParser(bot)
        self.user_roles_cache = {}

    async def log_role_add_event(self, member, role):
        try:
            if not member.guild:
                return
                
            guild_data = get_specific_field(member.guild.id, "audit_logs")
            if not guild_data or "add_usr_rol" not in guild_data:
                return
            
            add_role_config = guild_data["add_usr_rol"]
            
            is_activated = add_role_config.get("activated")
            if isinstance(is_activated, str):
                is_activated = is_activated.lower() == "true"
            
            if not is_activated:
                return
                
            log_channel_id = add_role_config.get("log_channel")
            if not log_channel_id or log_channel_id == 0:
                return
            
            log_channel = self.bot.get_channel(int(log_channel_id))
            if not log_channel:
                return
            
            message_data = add_role_config.get("message", {})
            message_format = add_role_config.get("add_usr_rol_messages", "")
            
            if message_data and isinstance(message_data, dict):
                await self.log_parser.parse_and_send_log(
                    log_type="add_usr_rol",
                    log_channel=log_channel,
                    message_format=message_data,
                    member=member,
                    role=role,
                    guild=member.guild
                )
            elif message_format:
                await self.log_parser.parse_and_send_log(
                    log_type="add_usr_rol",
                    log_channel=log_channel,
                    message_format=message_format,
                    member=member,
                    role=role,
                    guild=member.guild
                )
            else:
                embed = discord.Embed(
                    title="Rol Añadido",
                    description=f"**Usuario:** {member.mention} ({member.id})\n**Rol:** {role.mention} ({role.id})",
                    color=role.color,
                    timestamp=discord.utils.utcnow()
                )
                
                await log_channel.send(embed=embed)

        except Exception as e:
            print(f"Error en log_role_add_event: {e}")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.roles != after.roles:
            added_roles = [role for role in after.roles if role not in before.roles]
            
            for role in added_roles:
                await self.log_role_add_event(after, role)

async def setup(bot):
    await bot.add_cog(AddedRolesLogs(bot))