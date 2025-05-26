import datetime
import re
from typing import Optional, Dict, Any

def parse_date(date_str: str) -> Optional[datetime.datetime]:
    if not date_str:
        return None
    
    date_patterns = [
        r'^(\d{1,2})/(\d{1,2})$',
        r'^(\d{1,2})-(\d{1,2})$', 
        r'^(\d{1,2})\.(\d{1,2})$'
    ]
    
    for pattern in date_patterns:
        match = re.match(pattern, date_str)
        if match:
            try:
                day = int(match.group(1))
                month = int(match.group(2))
                
                if month < 1 or month > 12:
                    return None
                
                max_days = 31
                if month in [4, 6, 9, 11]:
                    max_days = 30
                elif month == 2:
                    max_days = 29
                
                if day < 1 or day > max_days:
                    return None
                
                return datetime.datetime(2000, month, day)
            except ValueError:
                return None
    
    return None

def format_date(date: datetime.datetime) -> str:
    months = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    ]
    
    return f"{date.day} de {months[date.month-1]}"

def parse_timezone(timezone_str: str) -> Optional[int]:
    if not timezone_str:
        return None
    
    match = re.match(r'^([+-])(\d{1,2})(?::(\d{2}))?$', timezone_str)
    if not match:
        return None
    
    try:
        sign = 1 if match.group(1) == '+' else -1
        hours = int(match.group(2))
        minutes = int(match.group(3) or '0')
        
        if hours > 14 or minutes >= 60:
            return None
        
        return sign * (hours * 60 + minutes)
    except ValueError:
        return None

def get_user_timezone(timezone_minutes: int) -> str:
    sign = '+' if timezone_minutes >= 0 else '-'
    abs_minutes = abs(timezone_minutes)
    hours = abs_minutes // 60
    minutes = abs_minutes % 60
    
    return f"UTC{sign}{hours:02d}:{minutes:02d}"

def format_mentions(users, message: str) -> str:
    if len(users) == 1:
        return message.replace("[@users]", users[0].mention)
    
    mentions = [user.mention for user in users]
    if len(mentions) == 2:
        user_text = f"{mentions[0]} y {mentions[1]}"
    else:
        user_text = ", ".join(mentions[:-1]) + f" y {mentions[-1]}"
    
    return message.replace("[@users]", user_text)