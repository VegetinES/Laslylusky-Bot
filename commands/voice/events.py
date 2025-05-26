import discord
from discord.ext import commands, tasks
import asyncio
from .database import get_voice_config, get_voice_channels, save_voice_channel, delete_voice_channel
from .permissions import setup_channel_permissions
from .utils import create_channel_name
from .views.channel_view import create_channel_control_message

class VoiceEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.owner_timeout = {}
        self.check_empty_channels.start()
        self.check_owner_timeouts.start()
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return
            
        guild_id = member.guild.id
        config = get_voice_config(guild_id)
        
        if not config or not config.get("generator_channel"):
            return
        
        if after.channel and after.channel.id == config["generator_channel"]:
            await self.create_voice_channel(member, after.channel)
            return
            
        voice_channels = get_voice_channels(guild_id)
        
        if before.channel and str(before.channel.id) in voice_channels:
            channel_data = voice_channels[str(before.channel.id)]
            
            if channel_data.get("owner_id") == member.id:
                self.owner_timeout[before.channel.id] = {
                    "time": discord.utils.utcnow().timestamp(),
                    "owner_id": member.id
                }
            
            if len(before.channel.members) == 0:
                await self.delete_empty_channel(before.channel, guild_id)
        
        if after.channel and str(after.channel.id) in voice_channels:
            channel_data = voice_channels[str(after.channel.id)]
            
            if channel_data.get("owner_id") == member.id and after.channel.id in self.owner_timeout:
                del self.owner_timeout[after.channel.id]
    
    async def create_voice_channel(self, member, generator_channel):
        guild = member.guild
        guild_id = guild.id
        config = get_voice_config(guild_id)
        
        category_id = config.get("category_id", generator_channel.category_id if generator_channel.category else None)
        category = guild.get_channel(category_id) if category_id else None
        
        channel_name = create_channel_name(member)
        bitrate = config.get("default_bitrate", 64000)
        user_limit = config.get("default_user_limit", 0)
        
        try:
            channel = await guild.create_voice_channel(
                name=channel_name,
                category=category,
                bitrate=bitrate,
                user_limit=user_limit,
                reason=f"Canal de voz creado para {member.name}"
            )
            
            await setup_channel_permissions(channel, member, config.get("admin_roles", []))
            
            await member.move_to(channel)
            
            save_voice_channel(guild_id, channel.id, {
                "owner_id": member.id,
                "created_at": discord.utils.utcnow().timestamp(),
                "name": channel_name,
                "privacy": "public",
                "visibility": "visible",
                "allowed_users": [],
                "managers": []
            })
            
            await create_channel_control_message(channel)
            
            return True
        except Exception as e:
            print(f"Error al crear canal de voz: {e}")
            return False
    
    async def delete_empty_channel(self, channel, guild_id):
        voice_channels = get_voice_channels(guild_id)
        channel_data = voice_channels.get(str(channel.id))
        
        if not channel_data:
            return
            
        await asyncio.sleep(2)
        
        try:
            channel = await channel.guild.fetch_channel(channel.id)
            if len(channel.members) > 0:
                return
        except discord.NotFound:
            delete_voice_channel(guild_id, channel.id)
            return
            
        try:
            await channel.delete(reason="Canal de voz dinámico vacío")
        except discord.HTTPException:
            pass
            
        delete_voice_channel(guild_id, channel.id)
        
        if channel.id in self.owner_timeout:
            del self.owner_timeout[channel.id]
    
    async def transfer_ownership(self, channel_id, guild_id):
        try:
            voice_channels = get_voice_channels(guild_id)
            if str(channel_id) not in voice_channels:
                return False
                
            channel_data = voice_channels[str(channel_id)]
            guild = self.bot.get_guild(guild_id)
            if not guild:
                return False
                
            channel = guild.get_channel(channel_id)
            if not channel or len(channel.members) == 0:
                return False
            
            new_owner = None
            
            allowed_users = channel_data.get("allowed_users", [])
            for user_id in allowed_users:
                member = guild.get_member(user_id)
                if member and member in channel.members:
                    new_owner = member
                    break
            
            if not new_owner and channel.members:
                new_owner = channel.members[0]
            
            if not new_owner:
                return False
            
            channel_data["owner_id"] = new_owner.id
            save_voice_channel(guild_id, channel_id, channel_data)
            
            await channel.send(
                f"📢 **{new_owner.mention} es ahora el propietario de este canal.**\n"
                f"Puede usar los botones del mensaje anclado para gestionar el canal."
            )
            
            await create_channel_control_message(channel, update=True)
            
            return True
        except Exception as e:
            print(f"Error al transferir propiedad: {e}")
            return False
    
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        if not isinstance(channel, discord.VoiceChannel):
            return
            
        guild_id = channel.guild.id
        voice_channels = get_voice_channels(guild_id)
        
        if str(channel.id) in voice_channels:
            delete_voice_channel(guild_id, channel.id)
            
            if channel.id in self.owner_timeout:
                del self.owner_timeout[channel.id]
    
    @tasks.loop(minutes=1)
    async def check_owner_timeouts(self):
        current_time = discord.utils.utcnow().timestamp()
        
        for channel_id, data in list(self.owner_timeout.items()):
            if current_time - data["time"] >= 600:
                guild_id = None
                
                for guild in self.bot.guilds:
                    channel = guild.get_channel(channel_id)
                    if channel:
                        guild_id = guild.id
                        break
                
                if guild_id:
                    await self.transfer_ownership(channel_id, guild_id)
                
                del self.owner_timeout[channel_id]
    
    @tasks.loop(minutes=5)
    async def check_empty_channels(self):
        for guild in self.bot.guilds:
            voice_channels = get_voice_channels(guild.id)
            
            for channel_id, data in list(voice_channels.items()):
                channel = guild.get_channel(int(channel_id))
                
                if not channel or len(channel.members) == 0:
                    await self.delete_empty_channel(channel, guild.id)

    @check_empty_channels.before_loop
    @check_owner_timeouts.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(VoiceEvents(bot))