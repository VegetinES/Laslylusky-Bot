from .connection import firebase_db

def save_server_data(guild, data):
    try:
        ref = firebase_db.get_reference()
        ref.child(str(guild.id)).set(data)
        return True
    except Exception as e:
        print(f"Error al guardar datos: {e}")
        return False