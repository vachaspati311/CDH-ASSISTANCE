import os
import sys
import logging
import time
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

orchestrator = None
chroma_manager = None

def wait_for_chroma(max_retries=30):
    """Wait for ChromaDB to be ready"""
    import requests
    chroma_url = f"http://{os.getenv('CHROMA_HOST', 'chromadb')}:{os.getenv('CHROMA_PORT', '8000')}"
    
    for i in range(max_retries):
        try:
            response = requests.get(f"{chroma_url}/api/v1/heartbeat", timeout=5)
            if response.status_code == 200:
                logger.info("✅ ChromaDB is ready")
                return True
        except:
            pass
        
        logger.info(f"⏳ Waiting for ChromaDB... ({i+1}/{max_retries})")
        time.sleep(2)
    
    return False

@asynccontextmanager
async def lifespan(app: FastAPI):
    global orchestrator, chroma_manager
    
    logger.info("🚀 Initializing Pega CDH Upgrade Assistant...")
    
    # Wait for ChromaDB
    if not wait_for_chroma():
        logger.error("❌ ChromaDB failed to start")
        raise Exception("ChromaDB not available")
    
    try:
        from vectorstore.chroma_manager import ChromaManager
        from agents.orchestrator import AgentOrchestrator
        
        chroma_manager = ChromaManager()
        orchestrator = AgentOrchestrator(chroma_manager)
        
        logger.info("✅ System ready")
    except Exception as e:
        logger.error(f"❌ Initialization failed: {e}")
        raise
    
    yield
    
    logger.info("🛑 Shutting down...")

app = FastAPI(
    title="Pega CDH Upgrade Assistant API",
    version="2.1.1",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResearchRequest(BaseModel):
    query: str
    depth: int = 3

class UpgradePlanRequest(BaseModel):
    current_version: str = "8.7.1"
    target_version: str = "25.1"
    environment: str = "openshift"
    cdh_enabled: bool = True

@app.get("/health")
async def health_check():
    return {
        "status": "healthy" if orchestrator else "initializing",
        "version": "2.1.1",
        "agents_ready": orchestrator is not None,
        "vector_store": chroma_manager.get_stats() if chroma_manager else None
    }

@app.post("/research")
async def deep_research(request: ResearchRequest):
    if not orchestrator:
        raise HTTPException(status_code=503, detail="System not initialized")
    result = await orchestrator.research(request.query, request.depth)
    return result

@app.post("/upgrade-plan")
async def generate_upgrade_plan(request: UpgradePlanRequest):
    if not orchestrator:
        raise HTTPException(status_code=503, detail="System not initialized")
    plan = await orchestrator.create_upgrade_plan(
        request.current_version, request.target_version,
        request.environment, request.cdh_enabled
    )
    return plan

@app.post("/scrape")
async def trigger_scraping(background_tasks: BackgroundTasks):
    if not orchestrator:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    async def scrape_task():
        await orchestrator.scrape_documentation()
    
    background_tasks.add_task(scrape_task)
    return {"status": "started"}

@app.get("/agents")
async def list_agents():
    if not orchestrator:
        raise HTTPException(status_code=503, detail="System not initialized")
    return orchestrator.list_agents()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
