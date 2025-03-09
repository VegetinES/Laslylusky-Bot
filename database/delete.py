from .connection import firebase_db

def delete_server_data(guild_id):
    try:
        ref = firebase_db.get_reference()
        ref.child(str(guild_id)).delete()
        return True
    except Exception as e:
        print(f"Error al eliminar datos: {e}")
        return False

def delete_field(guild_id, path):
    try:
        ref = firebase_db.get_reference()
        ref.child(str(guild_id)).child(path).delete()
        return True
    except Exception as e:
        print(f"Error al eliminar campo: {e}")
        return False