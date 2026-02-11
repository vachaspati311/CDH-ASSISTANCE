from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class Document(BaseModel):
    id: Optional[str] = None
    content: str
    metadata: Dict[str, Any] = {}
    source: str
    title: Optional[str] = None
    category: Optional[str] = None
    created_at: Optional[str] = None
    
    def __init__(self, **data):
        if 'created_at' not in data:
            data['created_at'] = datetime.now().isoformat()
        super().__init__(**data)
