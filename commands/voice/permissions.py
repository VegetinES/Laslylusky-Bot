import discord
import asyncio
from .database import get_voice_channels, save_voice_channel
from typing import Optional

async def setup_channel_permissions(channel, owner, admin_roles):
    await channel.set_permissions(
        channel.guild.default_role,
        connect=True,
        speak=True,
        stream=True,
        use_voice_activation=True,
        create_instant_invite=False,
        manage_channels=False,
        manage_permissions=False,
    )
    
    await channel.set_permissions(
        owner,
        connect=True,
        speak=True,
        stream=True,
        use_voice_activation=True,
        create_instant_invite=True,
        manage_channels=True,
        manage_permissions=True,
        move_members=True,
        mute_members=True,
        deafen_members=True,
        priority_speaker=True
    )
    
    for role_id in admin_roles:
        role = channel.guild.get_role(role_id)
        if role:
            await channel.set_permissions(
                role,
                connect=True,
                speak=True,
                stream=True,
                use_voice_activation=True,
                create_instant_invite=True,
                manage_channels=True,
                manage_permissions=True,
                move_members=True,
                mute_members=True,
                deafen_members=True
            )

async def add_user_to_channel(channel, user, guild_id, permission_level="viewer"):
    try:
        voice_channels = get_voice_channels(guild_id)
        channel_data = voice_channels.get(str(channel.id))
        
        if not channel_data:
            return False
        
        if permission_level == "viewer":
            await channel.set_permissions(
                user,
                connect=True,
                speak=True,
                stream=True,
                use_voice_activation=True
            )
        elif permission_level == "moderator":
            await channel.set_permissions(
                user,
                connect=True, 
                speak=True,
                stream=True,
                use_voice_activation=True,
                move_members=True,
                mute_members=True,
                deafen_members=True
            )
        elif permission_level == "co-owner":
            await channel.set_permissions(
                user,
                connect=True,
                speak=True,
                stream=True,
                use_voice_activation=True,
                create_instant_invite=True,
                manage_channels=True,
                move_members=True,
                mute_members=True,
                deafen_members=True,
                priority_speaker=True
            )
        
        if "user_permissions" not in channel_data:
            channel_data["user_permissions"] = {}
            
        channel_data["user_permissions"][str(user.id)] = permission_level
        save_voice_channel(guild_id, channel.id, channel_data)
        
        return True
        
    except discord.HTTPException:
        return False

async def remove_user_from_channel(channel, user, guild_id):
    try:
        voice_channels = get_voice_channels(guild_id)
        channel_data = voice_channels.get(str(channel.id))
        
        if not channel_data:
            return False
        
        await channel.set_permissions(user, overwrite=None)
        
        if "user_permissions" in channel_data and str(user.id) in channel_data["user_permissions"]:
            del channel_data["user_permissions"][str(user.id)]
            save_voice_channel(guild_id, channel.id, channel_data)
        
        if user in channel.members:
            try:
                if channel.guild.afk_channel:
                    await user.move_to(channel.guild.afk_channel)
                else:
                    await user.move_to(None)
            except discord.HTTPException:
                pass
        
        return True
        
    except discord.HTTPException:
        return False

async def add_role_to_channel(channel, role, guild_id, permission_level="viewer"):
    try:
        voice_channels = get_voice_channels(guild_id)
        channel_data = voice_channels.get(str(channel.id))
        
        if not channel_data:
            return False
        
        if permission_level == "viewer":
            await channel.set_permissions(
                role,
                connect=True,
                speak=True,
                stream=True,
                use_voice_activation=True
            )
        elif permission_level == "moderator":
            await channel.set_permissions(
                role,
                connect=True, 
                speak=True,
                stream=True,
                use_voice_activation=True,
                move_members=True,
                mute_members=True,
                deafen_members=True
            )
        elif permission_level == "co-owner":
            await channel.set_permissions(
                role,
                connect=True,
                speak=True,
                stream=True,
                use_voice_activation=True,
                create_instant_invite=True,
                manage_channels=True,
                move_members=True,
                mute_members=True,
                deafen_members=True,
                priority_speaker=True
            )
        
        if "role_permissions" not in channel_data:
            channel_data["role_permissions"] = {}
            
        channel_data["role_permissions"][str(role.id)] = permission_level
        save_voice_channel(guild_id, channel.id, channel_data)
        
        return True
        
    except discord.HTTPException:
        return False