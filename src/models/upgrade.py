from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class UpgradePhase(BaseModel):
    name: str
    duration: str
    tasks: List[str] = []
    cdh_specific: Optional[List[str]] = None

class UpgradePlan(BaseModel):
    plan_id: str
    current_version: str
    target_version: str
    environment: str
    cdh_enabled: bool = True
    phases: List[UpgradePhase] = []
    timeline: str
    risks: List[Dict[str, Any]] = []
    prerequisites: List[str] = []
    validation_steps: List[str] = []
    rollback_strategy: str
    created_at: str = datetime.now().isoformat()
