from .connection import mongo_db
from pymongo.errors import PyMongoError

def update_server_data(guild_id, path, value):
    try:
        collection = mongo_db.get_collection()
        
        update_query = {f"$set": {path: value}}
        
        result = collection.update_one(
            {'_id': str(guild_id)},
            update_query
        )
        
        return result.modified_count > 0 or result.matched_count > 0
    except PyMongoError as e:
        print(f"Error al actualizar datos: {e}")
        return False
    except Exception as e:
        print(f"Error al actualizar datos: {e}")
        return False

def update_multiple_fields(guild_id, updates):
    try:
        collection = mongo_db.get_collection()
        
        update_query = {"$set": updates}
        
        result = collection.update_one(
            {'_id': str(guild_id)},
            update_query
        )
        
        return result.modified_count > 0 or result.matched_count > 0
    except PyMongoError as e:
        print(f"Error al actualizar múltiples campos: {e}")
        return False
    except Exception as e:
        print(f"Error al actualizar múltiples campos: {e}")
        return False