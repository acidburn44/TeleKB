import json
import os

class Settings:
    FILE_PATH = "settings.json"
    
    def __init__(self):
        self.data = self._load()
        
    def _load(self):
        if not os.path.exists(self.FILE_PATH):
            return {}
        try:
            with open(self.FILE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}

    def save(self):
        try:
            with open(self.FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
        except OSError:
            pass
            
    def get(self, key, default=None):
        return self.data.get(key, default)
        
    def set(self, key, value):
        self.data[key] = value
        self.save()
