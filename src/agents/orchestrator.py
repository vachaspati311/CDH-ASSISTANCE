# src/agents/orchestrator.py
import asyncio
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

from .research_agent import ResearchAgent
from .upgrade_planner import UpgradePlannerAgent
from .risk_analyzer import RiskAnalyzerAgent
from .openshift_specialist import OpenShiftSpecialistAgent
from .cdh_specialist import CDHSpecialistAgent
from .migration_agent import MigrationAgent

@dataclass
class AgentTask:
    agent_type: str
    task: str
    context: Dict[str, Any]
    priority: int = 1

class AgentOrchestrator:
    """Supervisor agent that coordinates multiple specialized agents"""
    
    def __init__(self, chroma_manager):
        self.chroma = chroma_manager
        
        self.agents = {
            "research": ResearchAgent(chroma_manager),
            "upgrade_planner": UpgradePlannerAgent(chroma_manager),
            "risk_analyzer": RiskAnalyzerAgent(chroma_manager),
            "openshift": OpenShiftSpecialistAgent(chroma_manager),
            "cdh": CDHSpecialistAgent(chroma_manager),
            "migration": MigrationAgent(chroma_manager)
        }
        
        self.active_tasks: List[AgentTask] = []
    
    async def research(self, query: str, depth: int = 3, 
                       sources: Optional[List[str]] = None) -> Dict:
        """Deep research using ResearchAgent"""
        research_tasks = [
            self.agents["research"].web_search(query, depth),
            self.agents["research"].documentation_search(query),
            self.agents["research"].community_search(query)
        ]
        
        if "openshift" in query.lower() or "kubernetes" in query.lower():
            research_tasks.append(self.agents["openshift"].research(query))
        
        if "cdh" in query.lower() or "decision" in query.lower():
            research_tasks.append(self.agents["cdh"].research(query))
        
        results = await asyncio.gather(*research_tasks, return_exceptions=True)
        
        synthesis = await self._synthesize_research(results, query)
        
        return {
            "query": query,
            "depth": depth,
            "findings": synthesis,
            "sources": self._extract_sources(results),
            "confidence_score": self._calculate_confidence(results)
        }
    
    async def create_upgrade_plan(self, current: str, target: str,
                                  environment: str, cdh_enabled: bool,
                                  constraints: Optional[List[str]] = None) -> Dict:
        """Create comprehensive upgrade plan"""
        analysis_tasks = {
            "risks": self.agents["risk_analyzer"].analyze_upgrade_path(current, target),
            "infrastructure": self.agents["openshift"].assess_infrastructure(environment),
            "cdh_specifics": self.agents["cdh"].analyze_upgrade_impact() if cdh_enabled else None,
            "timeline": self.agents["upgrade_planner"].estimate_timeline(current, target, constraints),
            "dependencies": self.agents["upgrade_planner"].map_dependencies(current, target)
        }
        
        results = {}
        for key, task in analysis_tasks.items():
            if task:
                results[key] = await task
        
        plan = await self.agents["upgrade_planner"].create_comprehensive_plan(
            current=current, target=target, environment=environment,
            analysis_results=results, constraints=constraints
        )
        
        return {
            "plan_id": f"plan_{current}_to_{target}_{hash(str(constraints))}",
            "current_version": current,
            "target_version": target,
            "environment": environment,
            "cdh_enabled": cdh_enabled,
            "phases": plan["phases"],
            "timeline": plan["timeline"],
            "risks": results["risks"],
            "prerequisites": plan["prerequisites"],
            "validation_steps": plan["validation"],
            "rollback_strategy": plan["rollback"]
        }
    
    async def analyze(self, component: str, analysis_type: str) -> Dict:
        """Component-specific analysis"""
        if "openshift" in component.lower() or "k8s" in component.lower():
            agent = self.agents["openshift"]
        elif "cdh" in component.lower() or "decision" in component.lower():
            agent = self.agents["cdh"]
        elif "migration" in analysis_type:
            agent = self.agents["migration"]
        else:
            agent = self.agents["risk_analyzer"]
        
        return await agent.analyze_component(component, analysis_type)
    
    async def scrape_documentation(self, force_full: bool = False,
                                   sources: Optional[List[str]] = None) -> Dict:
        """Comprehensive documentation scraping"""
        scraper_agents = [
            self.agents["research"],
            self.agents["openshift"],
            self.agents["cdh"]
        ]
        
        scrape_tasks = [agent.scrape(sources, force_full) for agent in scraper_agents]
        results = await asyncio.gather(*scrape_tasks)
        
        total_docs = sum(r.get("documents", 0) for r in results if isinstance(r, dict))
        
        return {
            "status": "completed",
            "documents_scraped": total_docs,
            "sources": [r.get("source") for r in results],
            "details": results
        }
    
    async def query(self, query: str, agent_type: Optional[str] = None) -> str:
        """Simple query routing"""
        if agent_type and agent_type in self.agents:
            agent = self.agents[agent_type]
        else:
            agent = self._route_query(query)
        
        return await agent.answer(query)
    
    def _route_query(self, query: str) -> Any:
        """Intelligent query routing"""
        query_lower = query.lower()
        
        if any(k in query_lower for k in ["openshift", "kubernetes", "k8s", "pod"]):
            return self.agents["openshift"]
        elif any(k in query_lower for k in ["cdh", "decision", "nba", "next-best"]):
            return self.agents["cdh"]
        elif any(k in query_lower for k in ["risk", "deprecated", "breaking"]):
            return self.agents["risk_analyzer"]
        elif any(k in query_lower for k in ["plan", "upgrade", "migrate"]):
            return self.agents["upgrade_planner"]
        else:
            return self.agents["research"]
    
    async def _synthesize_research(self, results: List[Any], original_query: str) -> str:
        """Synthesize research from multiple sources"""
        return await self.agents["upgrade_planner"].synthesize_findings(results, original_query)
    
    def _extract_sources(self, results: List[Any]) -> List[str]:
        """Extract unique sources"""
        sources = set()
        for r in results:
            if isinstance(r, dict) and "sources" in r:
                sources.update(r["sources"])
        return list(sources)
    
    def _calculate_confidence(self, results: List[Any]) -> float:
        """Calculate confidence score"""
        return 0.85
    
    def list_agents(self) -> List[Dict]:
        """List available agents"""
        return [
            {
                "name": name,
                "description": agent.description,
                "capabilities": agent.capabilities
            }
            for name, agent in self.agents.items()
        ]