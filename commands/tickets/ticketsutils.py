import discord
from discord import app_commands
from database.get import get_server_data, get_specific_field
import re
from database.update import update_server_data

COLORS = {
    "rojo": 0xe74c3c,
    "verde": 0x2ecc71,
    "azul": 0x3498db,
    "amarillo": 0xf1c40f,
    "naranja": 0xe67e22,
    "morado": 0x9b59b6,
    "rosa": 0xff6b81,
    "gris": 0x95a5a6,
    "negro": 0x34495e,
    "blanco": 0xecf0f1,
    "aleatorio": -1
}

CONFIG_STATE = {
    "NO_CONFIGURADO": 0,
    "CANAL_CONFIGURADO": 1,
    "PERMISOS_CONFIGURADOS": 2,
    "COMPLETAMENTE_CONFIGURADO": 3
}

async def channel_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    try:
        server_data = get_server_data(interaction.guild.id)
        if not server_data or "tickets" not in server_data:
            return []
        
        tickets_data = server_data["tickets"]
        
        choices = []
        for channel_id, data in tickets_data.items():
            if not channel_id.isdigit() or data.get("_removed"):
                continue
                
            tickets_name = data.get("tickets-name", "Ticket")
            channel = interaction.guild.get_channel(int(channel_id))
            if channel:
                display_name = f"{channel.name} - {tickets_name}"
                if current.lower() in display_name.lower():
                    choices.append(app_commands.Choice(name=display_name, value=channel_id))
        
        return choices[:25]
    except Exception as e:
        print(f"Error en channel_autocomplete: {e}")
        return []

async def color_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    return [
        app_commands.Choice(name=name, value=name)
        for name in COLORS.keys()
        if current.lower() in name.lower()
    ][:25]

def hex_to_int(hex_color: str) -> int:
    hex_color = hex_color.lstrip('#')
    return int(hex_color, 16)

def is_valid_hex_color(value: str) -> bool:
    if not value.startswith('#'):
        return False
    hex_color = value.lstrip('#')
    return len(hex_color) == 6 and all(c in '0123456789ABCDEFabcdef' for c in hex_color)

def parse_color(color_value: str) -> int:
    if color_value.lower() in COLORS:
        if color_value.lower() == "aleatorio":
            import random
            return random.randint(0, 0xFFFFFF)
        return COLORS[color_value.lower()]
    elif is_valid_hex_color(color_value):
        return hex_to_int(color_value)
    return 0x3498db

def get_ticket_config_state(guild_id: int, channel_id: str) -> int:
    server_data = get_server_data(guild_id)

    if not server_data or "tickets" not in server_data:
        return CONFIG_STATE["NO_CONFIGURADO"]

    if channel_id not in server_data["tickets"]:
        return CONFIG_STATE["NO_CONFIGURADO"]
    
    channel_config = server_data["tickets"][channel_id]

    if channel_config.get("_removed"):
        return CONFIG_STATE["NO_CONFIGURADO"]

    if "setup_stage" in channel_config:
        return channel_config["setup_stage"]

    perms_config = channel_config.get("perms", {})

    manage_roles = perms_config.get("manage-roles", [0])
    manage_users = perms_config.get("manage-users", [0])
    
    has_manage_perms = False
    
    if manage_roles != [0]:
        for role_id in manage_roles:
            if role_id != 0:
                has_manage_perms = True
                break
                
    if not has_manage_perms and manage_users != [0]:
        for user_id in manage_users:
            if user_id != 0:
                has_manage_perms = True
                break

    if not has_manage_perms:
        channel_config["setup_stage"] = CONFIG_STATE["CANAL_CONFIGURADO"]
        update_server_data(guild_id, f"tickets/{channel_id}", channel_config)
        return CONFIG_STATE["CANAL_CONFIGURADO"]
    
    has_open_ticket_msg = channel_config.get("ticket-abierto", {}).get("activado", False)
    has_ticket_button = channel_config.get("ticket-abrir", False)

    if not has_open_ticket_msg or not has_ticket_button:
        channel_config["setup_stage"] = CONFIG_STATE["PERMISOS_CONFIGURADOS"]
        update_server_data(guild_id, f"tickets/{channel_id}", channel_config)
        return CONFIG_STATE["PERMISOS_CONFIGURADOS"]
    
    channel_config["setup_stage"] = CONFIG_STATE["COMPLETAMENTE_CONFIGURADO"]
    update_server_data(guild_id, f"tickets/{channel_id}", channel_config)
    return CONFIG_STATE["COMPLETAMENTE_CONFIGURADO"]