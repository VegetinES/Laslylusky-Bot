import discord
import datetime
from datetime import timezone

async def can_dm_user(user):
    try:
        dm_channel = await user.create_dm()
        return True
    except discord.Forbidden:
        return False
    except Exception as e:
        return False

def format_reminder_time(reminder_time):
    now = datetime.datetime.now(timezone.utc)
    
    delta_days = (reminder_time.date() - now.date()).days
    
    if delta_days == 0:
        date_str = "Hoy"
    elif delta_days == 1:
        date_str = "Mañana"
    elif delta_days > 1 and delta_days < 7:
        days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        date_str = f"Este {days[reminder_time.weekday()]}"
    else:
        date_str = reminder_time.strftime("%d/%m/%Y")
    
    time_str = reminder_time.strftime("%H:%M")
    
    return f"{date_str} a las {time_str} UTC"

def validate_date_format(date_str):
    try:
        day, month, year = map(int, date_str.split('/'))
        
        if not (1 <= day <= 31 and 1 <= month <= 12 and year >= 2023):
            return False
        
        if month in [4, 6, 9, 11] and day > 30:
            return False
        
        if month == 2:
            is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
            if day > 29 or (not is_leap and day > 28):
                return False
        
        return True
    except (ValueError, IndexError):
        return False

def validate_time_format(time_str):
    try:
        hour, minute = map(int, time_str.split(':'))
        return 0 <= hour <= 23 and 0 <= minute <= 59
    except (ValueError, IndexError):
        return False

def validate_timezone_format(timezone_str):
    try:
        if timezone_str[0] not in ('+', '-'):
            return False
        
        parts = timezone_str[1:].split(':')
        if len(parts) != 2:
            return False
        
        hour, minute = map(int, parts)
        return 0 <= hour <= 14 and 0 <= minute <= 59
    except (ValueError, IndexError):
        return False

async def setup(bot):
    pass