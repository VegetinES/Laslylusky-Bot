import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

class Singleton:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        try:
            self.client = MongoClient(os.getenv("MONGO_URI"), server_api=ServerApi('1'))
            self.db = self.client['Lasly']
            self.servers_collection = self.db.servers
            
            self.client.admin.command('ping')
            print("Conexión a MongoDB")
        except Exception as e:
            print(f"Error de conexión a MongoDB: {e}")
            self.client = None
            self.db = None
            self.servers_collection = None
    
    def get_servers_collection(self):
        if self.servers_collection is None:
            raise Exception("Conexión con MongoDB no establecida")
        return self.servers_collection

database = Singleton()