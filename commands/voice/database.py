from database.get import get_specific_field
from database.update import update_server_data

def get_voice_config(guild_id):
    try:
        config = get_specific_field(guild_id, "voice_channels")
        if not config:
            config = {}
        return config
    except Exception as e:
        print(f"Error al obtener configuración de canales de voz: {e}")
        return {}

def save_voice_config(guild_id, config):
    try:
        return update_server_data(guild_id, "voice_channels", config)
    except Exception as e:
        print(f"Error al guardar configuración de canales de voz: {e}")
        return False

def get_voice_channels(guild_id):
    try:
        config = get_voice_config(guild_id)
        return config.get("channels", {})
    except Exception as e:
        print(f"Error al obtener lista de canales de voz: {e}")
        return {}

def save_voice_channel(guild_id, channel_id, channel_data):
    try:
        config = get_voice_config(guild_id)
        
        if "channels" not in config:
            config["channels"] = {}
            
        config["channels"][str(channel_id)] = channel_data
        return save_voice_config(guild_id, config)
    except Exception as e:
        print(f"Error al guardar canal de voz: {e}")
        return False

def delete_voice_channel(guild_id, channel_id):
    try:
        config = get_voice_config(guild_id)
        
        if "channels" in config and str(channel_id) in config["channels"]:
            del config["channels"][str(channel_id)]
            return save_voice_config(guild_id, config)
        return True
    except Exception as e:
        print(f"Error al eliminar canal de voz: {e}")
        return False

def get_user_channels(guild_id, user_id):
    try:
        channels = get_voice_channels(guild_id)
        user_channels = {}
        
        for channel_id, data in channels.items():
            if data.get("owner_id") == user_id:
                user_channels[channel_id] = data
                
        return user_channels
    except Exception as e:
        print(f"Error al obtener canales del usuario: {e}")
        return {}