import firebase_admin
from firebase_admin import credentials, db
import os

class FirebaseConnection:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseConnection, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        try:
            cred_dict = {
                "type": "service_account",
                "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
                "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
                "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
                "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
                "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL"),
                "universe_domain": "googleapis.com"
            }
            
            cred = credentials.Certificate(cred_dict)
            uid = os.getenv("FIREBASE_UID")
            dbURL = os.getenv("FIREBASE_DATABASE_URL")
            
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred, {
                    'databaseURL': dbURL,
                    'databaseAuthVariableOverride': {
                        'uid': uid
                    }
                })
            
            self.ref = db.reference('/resources')
            print("Conexión a Firebase establecida")
        except Exception as e:
            print(f"Error de conexión a Firebase: {e}")
            self.ref = None
    
    def get_reference(self):
        if self.ref is None:
            raise Exception("Conexión con Firebase no establecida")
        return self.ref

firebase_db = FirebaseConnection()