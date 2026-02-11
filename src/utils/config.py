import os
import yaml
from typing import Dict, Any

class Config:
    def __init__(self, config_dict: Dict[str, Any]):
        self._config = config_dict
        
        # App settings
        self.app = type('obj', (object,), config_dict.get('app', {}))
        
        # Pega settings
        self.pega = type('obj', (object,), config_dict.get('pega', {}))
        
        # AI settings
        self.ai = config_dict.get('ai', {})
        
        # Scraping settings
        self.scraping = config_dict.get('scraping', {})
        
        # Agents
        self.agents = config_dict.get('agents', {})
        
        # Vector store
        self.vectorstore = config_dict.get('vectorstore', {})

def load_config(config_path: str = "/app/config.yaml") -> Config:
    """Load configuration from YAML file"""
    if not os.path.exists(config_path):
        # Default config if file not found
        return Config({
            'app': {'name': 'Pega CDH Upgrade Assistant', 'version': '2.1.1'},
            'pega': {'source_version': '8.7.1', 'target_version': '25.1'},
            'ai': {
                'embedding': {'model': 'text-embedding-3-large'},
                'llm': {'model': 'llama3.1:8b'}
            }
        })
    
    with open(config_path, 'r') as f:
        config_dict = yaml.safe_load(f)
    
    return Config(config_dict)
