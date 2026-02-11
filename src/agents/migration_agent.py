from .base_agent import BaseAgent

class MigrationAgent(BaseAgent):
    """Agent for code and rule migration assistance"""
    
    def __init__(self, chroma_manager):
        super().__init__(chroma_manager)
        self.description = "Code and rule migration specialist"
        self.capabilities = [
            "rule_migration_assistance",
            "code_conversion",
            "deprecated_rule_detection"
        ]
    
    async def suggest_rule_migration(self, rule_name: str, rule_type: str) -> dict:
        """Suggest migration path for custom rules"""
        # Search for migration patterns
        query = f"{rule_type} {rule_name} migration 8.7 to inifinity 25.1"
        results = self.chroma.search(query, n_results=5)
        
        context = "\n".join([r["content"] for r in results])
        
        prompt = f"""
        Rule: {rule_name} (Type: {rule_type})
        Context: Migrating from Pega 8.7.1 to infinity 25.1
        
        Documentation: {context[:2000]}
        
        Provide:
        1. Is this rule type deprecated?
        2. New recommended approach in 25.1
        3. Migration steps
        """
        
        response = await self._call_ollama(prompt, task_type="coding")
        
        return {
            "rule_name": rule_name,
            "rule_type": rule_type,
            "migration_advice": response,
            "references": [r["metadata"] for r in results]
        }
    
    async def analyze_component(self, component: str, analysis_type: str) -> dict:
        """Analyze component for migration"""
        return {
            "component": component,
            "analysis_type": analysis_type,
            "status": "analysis_complete",
            "recommendations": []
        }
