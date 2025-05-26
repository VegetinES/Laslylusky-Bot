import discord
from .constants import calculate_xp_for_next_level, get_level_from_xp, LEVEL_COLORS, get_total_xp_for_level

def format_progress_bar(current, total, length=10):
    filled_length = int(length * current / total)
    bar = '█' * filled_length + '░' * (length - filled_length)
    percent = current / total * 100
    return bar, percent

def get_level_color(level):
    for min_level in sorted(list(LEVEL_COLORS.keys()), reverse=True):
        if level >= min_level:
            return LEVEL_COLORS[min_level]
    return LEVEL_COLORS[0]

def create_level_embed(user, user_data, rank, total_users):
    level = user_data["level"]
    xp = user_data["xp"]
    messages = user_data["messages"]
    
    next_level_xp = calculate_xp_for_next_level(level)
    
    total_xp_for_current_level = get_total_xp_for_level(level)
    xp_in_current_level = xp - total_xp_for_current_level
    
    level_progress, percent = format_progress_bar(xp_in_current_level, next_level_xp)
    
    embed = discord.Embed(
        title=f"Nivel de {user.display_name}",
        description=f"**Nivel:** {level}",
        color=get_level_color(level)
    )
    
    embed.add_field(name="Experiencia total", value=f"{xp:,} XP", inline=True)
    embed.add_field(name="Mensajes", value=f"{messages:,}", inline=True)
    embed.add_field(name="Posición", value=f"#{rank} de {total_users}", inline=True)
    
    embed.add_field(
        name=f"Progreso al nivel {level + 1}",
        value=f"{level_progress} {percent:.1f}%\n{xp_in_current_level:,}/{next_level_xp:,} XP",
        inline=False
    )
    
    embed.set_thumbnail(url=user.display_avatar.url)
    return embed

def create_leaderboard_embed(guild, users_data, page, total_pages):
    embed = discord.Embed(
        title=f"Top Niveles de {guild.name}",
        description=f"Página {page + 1}/{total_pages}",
        color=discord.Color.gold()
    )
    
    for i, user_data in enumerate(users_data):
        rank = i + 1 + (page * 10)
        level, _ = get_level_from_xp(user_data["xp"])
        
        medal = ""
        if rank == 1:
            medal = "🥇"
        elif rank == 2:
            medal = "🥈"
        elif rank == 3:
            medal = "🥉"
        
        user_id = user_data["user_id"]
        member = guild.get_member(user_id)
        
        if member:
            embed.add_field(
                name=f"{medal} #{rank} {member.display_name}",
                value=f"Nivel {level} | {user_data['xp']:,} XP | {user_data['messages']:,} mensajes",
                inline=False
            )
    
    embed.set_footer(text=f"Usa los botones para navegar por el ranking")
    return embed

async def has_level_admin_perms(interaction):
    if interaction.user.guild_permissions.administrator:
        return True
    
    try:
        from database.get import get_specific_field
        admin_roles = get_specific_field(interaction.guild.id, "perms/admin-roles") or []
        admin_users = get_specific_field(interaction.guild.id, "perms/admin-users") or []
        
        if interaction.user.id in admin_users:
            return True
        
        for role in interaction.user.roles:
            if role.id in admin_roles:
                return True
    except ImportError:
        pass
    
    return False

def parse_time_string(time_str):
    if not time_str:
        return None
    
    time_str = time_str.lower().strip()
    if not time_str[-1] in ["s", "m", "h", "d"]:
        return None
    
    try:
        value = int(time_str[:-1])
        unit = time_str[-1]
        
        if unit == "s":
            return value
        elif unit == "m":
            return value * 60
        elif unit == "h":
            return value * 3600
        elif unit == "d":
            return value * 86400
    except ValueError:
        return None