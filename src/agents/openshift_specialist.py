from .base_agent import BaseAgent

class OpenShiftSpecialistAgent(BaseAgent):
    def __init__(self, chroma_manager):
        super().__init__(chroma_manager)
        self.description = "OpenShift specialist"
    
    async def research(self, query: str) -> dict:
        return {}
    
    async def scrape(self, sources=None, force_full=False) -> dict:
        return {"agent": "openshift", "documents": 0}