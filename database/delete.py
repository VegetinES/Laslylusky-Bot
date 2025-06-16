from .connection import mongo_db
from pymongo.errors import PyMongoError

def delete_server_data(guild_id):
    try:
        collection = mongo_db.get_collection()
        result = collection.delete_one({'_id': str(guild_id)})
        return result.deleted_count > 0
    except PyMongoError as e:
        print(f"Error al eliminar datos: {e}")
        return False
    except Exception as e:
        print(f"Error al eliminar datos: {e}")
        return False

def delete_field(guild_id, path):
    try:
        collection = mongo_db.get_collection()
        
        unset_query = {"$unset": {path: ""}}
        
        result = collection.update_one(
            {'_id': str(guild_id)},
            unset_query
        )
        
        return result.modified_count > 0
    except PyMongoError as e:
        print(f"Error al eliminar campo: {e}")
        return False
    except Exception as e:
        print(f"Error al eliminar campo: {e}")
        return False