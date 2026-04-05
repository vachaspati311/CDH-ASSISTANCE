# Pega CDH Upgrade Assistant

An AI-powered assistant that scrapes Pega documentation, stores it in a vector database, and uses an LLM to answer upgrade-related questions — specifically for upgrading **Pega Customer Decision Hub (CDH) from 8.7.1 to Infinity 25.1** on OpenShift.

---

## How It Works

```
Pega Docs / Community
        │
        ▼
  Web Scrapers (Tavily, Playwright, Scrapy)
        │
        ▼
  ChromaDB (Vector Store)  ◄──  OpenAI Embeddings (text-embedding-3-large)
        │
        ▼
  Specialized AI Agents  ◄──  Ollama LLM (Llama 3.1 / CodeLlama)
        │
        ▼
  Streamlit UI  /  FastAPI REST API
```

1. **Scraping** — Multiple scrapers pull documentation from `docs.pega.com`, the Pega Helm Charts repo, and community sources.
2. **Embedding** — Documents are chunked and embedded using OpenAI's `text-embedding-3-large` model, then stored in ChromaDB.
3. **Retrieval** — When a query arrives, relevant chunks are retrieved from ChromaDB via semantic search.
4. **Generation** — A locally-running Ollama model (Llama 3.1 8B by default) uses the retrieved context to generate accurate, grounded answers.

---

## Features

- **Multi-agent orchestration** — Specialized agents for research, upgrade planning, risk analysis, CDH, and OpenShift topics
- **Semantic search** over scraped Pega documentation
- **Upgrade plan generation** — Phased plans with timelines, risks, prerequisites, and rollback strategies
- **Component analysis** — Deep-dive into CDH, Kafka, Hazelcast, SRS, OpenShift deployments, and more
- **Streamlit UI** for interactive use
- **FastAPI REST API** for programmatic access
- **Fully local LLM** via Ollama — no data leaves your machine for inference

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| API | FastAPI + Uvicorn |
| LLM (inference) | Ollama — Llama 3.1 8B / CodeLlama 7B |
| Embeddings | OpenAI `text-embedding-3-large` |
| Vector DB | ChromaDB 0.5 |
| Scrapers | Tavily, Playwright, Scrapy, BeautifulSoup |
| Containerization | Docker + Docker Compose |

---

## Prerequisites

- Docker & Docker Compose
- [Ollama](https://ollama.com/) installed (or use the Docker service)
- OpenAI API key (for embeddings only)
- Tavily API key (for web scraping)

---

## Quickstart

### 1. Clone the repository

```bash
git clone https://github.com/vachaspati311/CDH-ASSISTANCE.git
cd CDH-ASSISTANCE
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in:

```env
OPENAI_API_KEY=sk-...          # Required for embeddings
TAVILY_API_KEY=tvly-...        # Required for web scraping
CHROMA_HOST=chromadb
CHROMA_PORT=8000
OLLAMA_HOST=ollama
OLLAMA_MODEL=llama3.1:8b
```

### 3. Start all services

```bash
docker-compose up --build
```

This starts:
- **ChromaDB** on port `8000`
- **Ollama** on port `11434`
- **App** (Streamlit UI on `8501`, FastAPI on `8001`)

### 4. Pull the LLM models (first time only)

```bash
docker exec -it pega-ollama ollama pull llama3.1:8b
docker exec -it pega-ollama ollama pull codellama:7b
```

### 5. Scrape documentation

Trigger the initial scrape via the API:

```bash
curl -X POST http://localhost:8001/scrape
```

Or use the Streamlit UI at `http://localhost:8501`.

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | System health and vector store stats |
| `POST` | `/research` | Deep research on a topic |
| `POST` | `/upgrade-plan` | Generate a full upgrade plan |
| `POST` | `/scrape` | Trigger background documentation scraping |
| `GET` | `/agents` | List available agents and capabilities |

### Example: Generate an upgrade plan

```bash
curl -X POST http://localhost:8001/upgrade-plan \
  -H "Content-Type: application/json" \
  -d '{
    "current_version": "8.7.1",
    "target_version": "25.1",
    "environment": "openshift",
    "cdh_enabled": true
  }'
```

### Example: Ask a research question

```bash
curl -X POST http://localhost:8001/research \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the breaking changes in CDH Infinity 25.1?",
    "depth": 3
  }'
```

---

## Agents

| Agent | Responsibility |
|---|---|
| `ResearchAgent` | Web search via Tavily + Playwright; stores results in ChromaDB |
| `UpgradePlannerAgent` | Builds phased upgrade plans and timeline estimates |
| `RiskAnalyzerAgent` | Identifies deprecated features, breaking changes, and risk severity |
| `CDHSpecialistAgent` | CDH-specific expertise: NBA, adaptive models, decision strategies |
| `OpenShiftSpecialistAgent` | Kubernetes/OpenShift deployment, Helm charts, pod configuration |
| `MigrationAgent` | Data and schema migration guidance |
| `AgentOrchestrator` | Routes queries to the right agent(s) and synthesizes results |

---

## Configuration

Key settings in `config.yaml`:

```yaml
pega:
  source_version: "8.7.1"
  target_version: "25.1"

ai:
  embedding:
    model: "text-embedding-3-large"
  llm:
    primary_model: "llama3.1:8b"    # swap for a larger model if needed
    temperature: 0.1

vectorstore:
  chunk_size: 1000
  chunk_overlap: 200
  top_k: 10
```

---

## Project Structure

```
CDH-ASSISTANCE/
├── src/
│   ├── main.py                  # FastAPI application entry point
│   ├── agents/                  # Specialized AI agents
│   │   ├── orchestrator.py      # Multi-agent coordinator
│   │   ├── research_agent.py
│   │   ├── cdh_specialist.py
│   │   ├── openshift_specialist.py
│   │   ├── upgrade_planner.py
│   │   ├── risk_analyzer.py
│   │   └── migration_agent.py
│   ├── scrapers/                # Web scraping modules
│   │   ├── tavily_scraper.py
│   │   ├── playwright_scraper.py
│   │   └── sitemap_scraper.py
│   ├── vectorstore/             # ChromaDB integration
│   │   ├── chroma_manager.py
│   │   ├── embeddings.py
│   │   └── retrievers.py
│   ├── tools/                   # Agent tools (search, file, analysis)
│   └── utils/                   # Config, logging, helpers
├── frontend/
│   └── streamlit_app.py         # Streamlit UI
├── config.yaml                  # Main configuration
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## Upgrade Scope

This assistant is pre-configured for the following upgrade path:

- **Source**: Pega Platform + CDH `8.7.1`
- **Target**: Pega Infinity `25.1`
- **Deployment**: OpenShift / Kubernetes
- **Components**: CDH, Kafka, Hazelcast, SRS, Elasticsearch, Cassandra, PostgreSQL

---

## License

MIT
