from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

class MongoConnection:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoConnection, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        try:
            self.client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')
            self.db = self.client['discord_bot']
            self.collection = self.db['guilds']
            print("Conexión a MongoDB establecida")
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"Error de conexión a MongoDB: {e}")
            self.client = None
            self.db = None
            self.collection = None
    
    def get_collection(self):
        if self.collection is None:
            raise Exception("Conexión con MongoDB no establecida")
        return self.collection
    
    def get_database(self):
        if self.db is None:
            raise Exception("Conexión con MongoDB no establecida")
        return self.db
    
    def close_connection(self):
        if self.client:
            self.client.close()

mongo_db = MongoConnection()