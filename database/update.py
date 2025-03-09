from .connection import firebase_db

def update_server_data(guild_id, path, value):
    try:
        ref = firebase_db.get_reference()
        ref.child(str(guild_id)).child(path).update(value)
        return True
    except Exception as e:
        print(f"Error al actualizar datos: {e}")
        return False

def update_multiple_fields(guild_id, updates):
    try:
        ref = firebase_db.get_reference()
        ref.child(str(guild_id)).update(updates)
        return True
    except Exception as e:
        print(f"Error al actualizar múltiples campos: {e}")
        return False