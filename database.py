import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

class Database:
    def __init__(self):
        self.client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
        self.db = self.client['Lasly']

    def connection(self):
        try:
            self.client.admin.command('ping')
            print("Conexión exitosa a MongoDB")
        except Exception as e:
            print(f"Error al conectar a MongoDB: {e}")

    def get_collection(self):
        try:
            return self.db.servers
        except Exception as e:
            print(f"Error {e}")
            return