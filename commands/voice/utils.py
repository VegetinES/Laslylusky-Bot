import discord
import random

def create_channel_name(member):
    prefix = random.choice(["🔊", "🎮", "🎵", "🎤", "📢", "🔉", "🎧"])
    return f"{prefix} Canal de {member.display_name}"

def get_formatted_voice_settings(channel):
    settings = []
    
    settings.append(f"**Nombre:** {channel.name}")
    
    limit = "Sin límite" if channel.user_limit == 0 else str(channel.user_limit)
    settings.append(f"**Límite de usuarios:** {limit}")
    
    bitrate_kbps = channel.bitrate // 1000
    settings.append(f"**Calidad:** {bitrate_kbps} kbps")
    
    region = "Automática" if not channel.rtc_region else channel.rtc_region
    settings.append(f"**Región:** {region}")
    
    return "\n".join(settings)

def get_permission_emoji(permission_level):
    if permission_level == "co-owner":
        return "👑"
    elif permission_level == "moderator":
        return "🛡️"
    else:
        return "👁️"

def get_permission_description(permission_level):
    if permission_level == "co-owner":
        return "Propietario adjunto (puede modificar el canal y gestionar usuarios)"
    elif permission_level == "moderator":
        return "Moderador (puede silenciar/expulsar usuarios)"
    else:
        return "Espectador (puede unirse al canal)"

def get_channel_info_embed(channel, channel_data):
    embed = discord.Embed(
        title=f"Canal: {channel.name}",
        color=discord.Color.blue()
    )
    
    owner_id = channel_data.get("owner_id")
    if owner_id:
        owner = channel.guild.get_member(owner_id)
        embed.add_field(
            name="Propietario",
            value=owner.mention if owner else f"ID: {owner_id}",
            inline=True
        )
    
    created_at = channel_data.get("created_at")
    if created_at:
        time = discord.utils.format_dt(discord.utils.utcfromtimestamp(created_at), style="R")
        embed.add_field(
            name="Creado",
            value=time,
            inline=True
        )
    
    embed.add_field(
        name="Configuración",
        value=get_formatted_voice_settings(channel),
        inline=False
    )
    
    user_perms = channel_data.get("user_permissions", {})
    if user_perms:
        users_text = []
        for user_id, level in user_perms.items():
            user = channel.guild.get_member(int(user_id))
            emoji = get_permission_emoji(level)
            if user:
                users_text.append(f"{emoji} {user.mention}")
        
        if users_text:
            embed.add_field(
                name="Usuarios con permisos",
                value="\n".join(users_text),
                inline=False
            )
    
    role_perms = channel_data.get("role_permissions", {})
    if role_perms:
        roles_text = []
        for role_id, level in role_perms.items():
            role = channel.guild.get_role(int(role_id))
            emoji = get_permission_emoji(level)
            if role:
                roles_text.append(f"{emoji} {role.mention}")
        
        if roles_text:
            embed.add_field(
                name="Roles con permisos",
                value="\n".join(roles_text),
                inline=False
            )
    
    return embed