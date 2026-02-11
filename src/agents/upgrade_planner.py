from .base_agent import BaseAgent

class UpgradePlannerAgent(BaseAgent):
    def __init__(self, chroma_manager):
        super().__init__(chroma_manager)
        self.description = "Upgrade planning agent"