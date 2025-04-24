from datetime import datetime
import threading
import time

class EmbedCache:
    def __init__(self):
        self.cache = {}
        self.lock = threading.Lock()
        # Iniciar un hilo para limpiar automáticamente los códigos expirados
        self.cleanup_thread = threading.Thread(target=self._cleanup_expired_codes, daemon=True)
        self.cleanup_thread.start()
    
    def add_embed(self, code, data):
        """Añade un nuevo embed a la caché con un código específico."""
        with self.lock:
            self.cache[code] = data
    
    def get_embed(self, code):
        """Obtiene un embed de la caché usando su código."""
        with self.lock:
            data = self.cache.get(code)
            if data and datetime.now() > data.get("expires_at", datetime.now()):
                # Si el código ha expirado, eliminarlo y devolver None
                self.cache.pop(code, None)
                return None
            return data
    
    def remove_embed(self, code):
        """Elimina un embed de la caché."""
        with self.lock:
            self.cache.pop(code, None)
    
    def _cleanup_expired_codes(self):
        """Limpia periódicamente los códigos expirados de la caché."""
        while True:
            time.sleep(60)  # Comprueba cada minuto
            with self.lock:
                current_time = datetime.now()
                expired_codes = [
                    code for code, data in self.cache.items()
                    if current_time > data.get("expires_at", current_time)
                ]
                
                for code in expired_codes:
                    self.cache.pop(code, None)