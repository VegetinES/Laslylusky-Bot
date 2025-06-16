from .connection import mongo_db
from pymongo.errors import PyMongoError

def save_server_data(guild, data, guild_id=None):
    try:
        collection = mongo_db.get_collection()
        
        if guild_id is None:
            guild_id = str(guild.id)
        
        data['_id'] = guild_id
        
        collection.replace_one(
            {'_id': guild_id},
            data,
            upsert=True
        )
        return True
    except PyMongoError as e:
        print(f"Error al guardar datos: {e}")
        return False
    except Exception as e:
        print(f"Error al guardar datos: {e}")
        return False