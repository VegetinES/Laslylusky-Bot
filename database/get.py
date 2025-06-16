from .connection import mongo_db
from pymongo.errors import PyMongoError

def get_server_data(guild_id):
    try:
        collection = mongo_db.get_collection()
        return collection.find_one({'_id': str(guild_id)})
    except PyMongoError as e:
        print(f"Error al obtener datos: {e}")
        return None
    except Exception as e:
        print(f"Error al obtener datos: {e}")
        return None

def get_specific_field(guild_id, path):
    try:
        collection = mongo_db.get_collection()
        guild_data = collection.find_one({'_id': str(guild_id)})
        
        if guild_data is None:
            return None
        
        keys = path.split('.')
        current_data = guild_data
        
        for key in keys:
            if isinstance(current_data, dict) and key in current_data:
                current_data = current_data[key]
            else:
                return None
        
        return current_data
    except PyMongoError as e:
        print(f"Error al obtener campo específico: {e}")
        return None
    except Exception as e:
        print(f"Error al obtener campo específico: {e}")
        return None