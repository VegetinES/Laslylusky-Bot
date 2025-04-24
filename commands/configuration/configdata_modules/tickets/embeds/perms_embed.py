import discord
from datetime import datetime
from .....tickets.constants import PERMISSIONS_DESCRIPTIONS
from ..utils import format_list

async def create_ticket_perms_embed(channel_id, ticket_config, interaction):
    embed = discord.Embed(
        title="Permisos de tickets",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    
    channel = interaction.guild.get_channel(int(channel_id))
    
    embed.add_field(
        name="Canal de tickets",
        value=f"{channel.mention if channel else f'`Canal ID: {channel_id}`'}",
        inline=False
    )
    
    perms_config = ticket_config.get("permissions", {})
    
    for perm_type, perm_info in perms_config.items():
        perm_name = PERMISSIONS_DESCRIPTIONS.get(perm_type, {}).get("name", perm_type.capitalize())
        perm_desc = PERMISSIONS_DESCRIPTIONS.get(perm_type, {}).get("description", "")
        
        roles_list = perm_info.get("roles", [])
        users_list = perm_info.get("users", [])
        
        roles_text = format_list(
            roles_list, 
            lambda rid: interaction.guild.get_role(int(rid))
        )
        
        users_text = format_list(
            users_list,
            lambda uid: interaction.guild.get_member(int(uid))
        )
        
        embed.add_field(
            name=f"**{perm_name}**",
            value=f"{perm_desc}\n\n**Roles:**\n{roles_text}\n\n**Usuarios:**\n{users_text}",
            inline=False
        )
    
    embed.set_footer(text=f"Solicitado por {interaction.user.name}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
    return embed