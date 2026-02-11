from .base_agent import BaseAgent

class RiskAnalyzerAgent(BaseAgent):
    def __init__(self, chroma_manager):
        super().__init__(chroma_manager)
        self.description = "Risk analysis agent"