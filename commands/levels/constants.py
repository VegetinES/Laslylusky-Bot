import discord

XP_BASE = 3
XP_PER_WORD = 0.5
XP_MAX_WORDS = 30
XP_MIN = 3
XP_MAX = 25
XP_COOLDOWN = 15

DEFAULT_ANNOUNCEMENT_MESSAGE = "{usuario} has subido a nivel {nivel}!!"

DEFAULT_CONFIG = {
    "enabled": False,
    "multiplier": 1.0,
    "multiplier_end_time": None,
    "reward_roles": {},
    "excluded_roles": [],
    "excluded_channels": [],
    "announcement": {
        "enabled": False,
        "message": DEFAULT_ANNOUNCEMENT_MESSAGE,
        "channel_type": "same",
        "custom_channel_id": None
    }
}

MULTIPLIER_OPTIONS = [
    {"label": "x0.25", "value": 0.25, "style": discord.ButtonStyle.danger},
    {"label": "x0.5", "value": 0.5, "style": discord.ButtonStyle.danger}, 
    {"label": "x0.75", "value": 0.75, "style": discord.ButtonStyle.danger},
    {"label": "x1 (Normal)", "value": 1.0, "style": discord.ButtonStyle.secondary},
    {"label": "x1.25", "value": 1.25, "style": discord.ButtonStyle.primary},
    {"label": "x1.5", "value": 1.5, "style": discord.ButtonStyle.primary},
    {"label": "x1.75", "value": 1.75, "style": discord.ButtonStyle.primary},
    {"label": "x2", "value": 2.0, "style": discord.ButtonStyle.success},
    {"label": "x2.5", "value": 2.5, "style": discord.ButtonStyle.success},
    {"label": "x3", "value": 3.0, "style": discord.ButtonStyle.success}
]

def calculate_xp_for_next_level(level):
    return 5 * (level ** 2) + 50 * level + 100

def get_level_from_xp(xp):
    level = 0
    current_level_xp = 0
    
    while True:
        xp_needed = calculate_xp_for_next_level(level)
        if xp < current_level_xp + xp_needed:
            break
        current_level_xp += xp_needed
        level += 1
    
    return level, current_level_xp

def get_total_xp_for_level(level):
    total_xp = 0
    for l in range(level):
        total_xp += calculate_xp_for_next_level(l)
    return total_xp

LEVEL_COLORS = {
    0: discord.Color.light_grey(),
    5: discord.Color.green(),
    10: discord.Color.blue(),
    20: discord.Color.purple(),
    30: discord.Color.gold(),
    50: discord.Color.orange(),
    75: discord.Color.red(),
    100: discord.Color(0xE91E63)
}