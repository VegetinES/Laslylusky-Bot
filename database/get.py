from .connection import firebase_db

def get_server_data(guild_id):
    try:
        ref = firebase_db.get_reference()
        return ref.child(str(guild_id)).get()
    except Exception as e:
        print(f"Error al obtener datos: {e}")
        return None

def get_specific_field(guild_id, path):
    try:
        ref = firebase_db.get_reference()
        return ref.child(str(guild_id)).child(path).get()
    except Exception as e:
        print(f"Error al obtener campo específico: {e}")
        return None