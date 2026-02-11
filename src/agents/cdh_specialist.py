# src/agents/cdh_specialist.py
from typing import Dict, List, Any

from .base_agent import BaseAgent

class CDHSpecialistAgent(BaseAgent):
    """Customer Decision Hub specialist"""
    
    def __init__(self, chroma_manager):
        super().__init__(chroma_manager)
        self.description = "CDH (Customer Decision Hub) upgrade specialist"
        self.capabilities = [
            "real_time_events_analysis",
            "decisioning_flow_mapping",
            "adaptive_model_migration"
        ]
    
    async def research(self, query: str) -> Dict:
        """CDH-specific research"""
        cdh_query = f"CDH Customer Decision Hub {query} Pega"
        
        local_results = self.chroma.search(cdh_query, n_results=5)
        
        from tavily import TavilyClient
        tavily = TavilyClient(api_key=self._get_env("TAVILY_API_KEY"))
        web_results = tavily.search(cdh_query, max_results=5)
        
        return {
            "local_knowledge": [r["content"] for r in local_results],
            "web_results": web_results.get("results", []),
            "synthesis": await self._synthesize_cdh_findings(local_results, web_results)
        }
    
    async def analyze_upgrade_impact(self) -> Dict:
        """Analyze CDH-specific upgrade impacts"""
        queries = [
            "CDH real time events inifinity 25.1 changes",
            "Next Best Action designer infinity 25.1",
            "Adaptive models migration 8.7 to infinity 25",
            "CDH deprecated features infinity 25.1 from 8.7.1"
        ]
        
        findings = {}
        for query in queries:
            results = self.chroma.search(query, n_results=3)
            findings[query] = [r["content"] for r in results]
        
        critical_changes = {
            "real_time_data_streaming": {
                "change": "Real-time data streaming to cloud warehouses",
                "impact": "High - New capability",
                "action": "Evaluate cloud warehouse integration"
            },
            "stream_service": {
                "change": "Externalized Kafka required",
                "impact": "Critical - Must migrate",
                "action": "Implement external Kafka"
            }
        }
        
        return {
            "critical_changes": critical_changes,
            "raw_findings": findings,
            "recommendations": await self._generate_cdh_recommendations(findings)
        }
    
    async def _synthesize_cdh_findings(self, local, web) -> str:
        """Synthesize CDH findings"""
        prompt = f"""Synthesize CDH findings: Local: {local}, Web: {web}"""
        return await self._call_ollama(prompt)
    
    async def _generate_cdh_recommendations(self, findings: Dict) -> List[str]:
        """Generate recommendations"""
        return [
            "Audit real-time event configurations",
            "Test externalized Kafka",
            "Validate adaptive models"
        ]
    
    async def scrape(self, sources, force_full):
        """CDH-specific scraping"""
        # Use Playwright for Pega CDH docs
        from playwright.async_api import async_playwright
        
        docs = []
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            urls = [
                "https://docs.pega.com/bundle/customer-decision-hub/page/customer-decision-hub/update/cdh-update-intro.html"
            ]
            
            for url in urls:
                await page.goto(url)
                content = await page.content()
                docs.append({"url": url, "content": content, "source": "cdh_playwright"})
                await self._store_document(docs[-1])
            
            await browser.close()
        
        return {"agent": "cdh", "source": "playwright", "documents": len(docs)}