from datetime import datetime
import threading
import time

class EmbedCache:
    def __init__(self):
        self.cache = {}
        self.lock = threading.Lock()
        self.cleanup_thread = threading.Thread(target=self._cleanup_expired_codes, daemon=True)
        self.cleanup_thread.start()
    
    def add_embed(self, code, data):
        with self.lock:
            self.cache[code] = data
    
    def get_embed(self, code):
        with self.lock:
            data = self.cache.get(code)
            if data and datetime.now() > data.get("expires_at", datetime.now()):
                self.cache.pop(code, None)
                return None
            return data
    
    def remove_embed(self, code):
        with self.lock:
            self.cache.pop(code, None)
    
    def _cleanup_expired_codes(self):
        while True:
            time.sleep(60)
            with self.lock:
                current_time = datetime.now()
                expired_codes = [
                    code for code, data in self.cache.items()
                    if current_time > data.get("expires_at", current_time)
                ]
                
                for code in expired_codes:
                    self.cache.pop(code, None)