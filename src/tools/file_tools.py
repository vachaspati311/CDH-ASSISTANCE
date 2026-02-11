import json
from pathlib import Path

class FileTools:
    def __init__(self, base_path="/app/data/exports"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def save_json(self, filename, data):
        filepath = self.base_path / filename
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return str(filepath)
    
    def load_json(self, filename):
        filepath = self.base_path / filename
        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)
        return None
