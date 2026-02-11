from pydantic import BaseModel
from typing import List, Optional

class PegaComponent(BaseModel):
    name: str
    version: str
    status: str  # active, deprecated, removed
    migration_notes: Optional[str] = None

class CDHConfiguration(BaseModel):
    real_time_events_enabled: bool = True
    external_kafka: bool = False
    adaptive_models_count: int = 0
    nba_strategies: List[str] = []
