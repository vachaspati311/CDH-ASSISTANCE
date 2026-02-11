# src/agents/research_agent.py
import asyncio
from typing import List, Dict, Optional, Any
import hashlib
from datetime import datetime

from tavily import TavilyClient
from playwright.async_api import async_playwright

from .base_agent import BaseAgent

class ResearchAgent(BaseAgent):
    """
    Deep research agent using Tavily (AI search) and Playwright (browser automation)
    NO Firecrawl - replaced with open-source Playwright
    """
    
    def __init__(self, chroma_manager):
        super().__init__(chroma_manager)
        self.description = "Deep research using Tavily AI search and Playwright scraping"
        self.capabilities = ["web_search", "browser_automation", "documentation_analysis"]
        
        self.tavily = TavilyClient(api_key=self._get_env("TAVILY_API_KEY"))
    
    async def web_search(self, query: str, depth: int = 3) -> Dict:
        """Tavily AI search"""
        self.logger.info(f"🔍 Tavily search: {query}")
        
        response = self.tavily.search(
            query=query,
            search_depth="advanced" if depth > 2 else "basic",
            max_results=10 * depth,
            include_answer=True,
            include_raw_content=True,
            include_images=False
        )
        
        documents = []
        for result in response.get("results", []):
            doc = {
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "content": result.get("raw_content", result.get("content", "")),
                "score": result.get("score", 0),
                "source": "tavily"
            }
            documents.append(doc)
            await self._store_document(doc)
        
        return {
            "query": query,
            "documents": len(documents),
            "answer": response.get("answer", ""),
            "sources": [d["url"] for d in documents]
        }
    
    async def playwright_scrape(self, url: str, max_pages: int = 10) -> Dict:
        """
        Deep scraping using Playwright (open-source replacement for Firecrawl)
        """
        self.logger.info(f"🎭 Playwright scraping: {url}")
        
        documents = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            
            page = await context.new_page()
            
            try:
                await page.goto(url, wait_until="networkidle", timeout=60000)
                
                # Extract main content
                content = await self._extract_page_content(page)
                
                doc = {
                    "url": url,
                    "title": await page.title(),
                    "content": content,
                    "source": "playwright"
                }
                documents.append(doc)
                await self._store_document(doc)
                
                # Follow links if max_pages > 1
                if max_pages > 1:
                    links = await self._extract_links(page, url, max_pages - 1)
                    
                    for link in links:
                        try:
                            await page.goto(link, wait_until="networkidle", timeout=30000)
                            content = await self._extract_page_content(page)
                            
                            doc = {
                                "url": link,
                                "title": await page.title(),
                                "content": content,
                                "source": "playwright"
                            }
                            documents.append(doc)
                            await self._store_document(doc)
                            
                            await asyncio.sleep(1)  # Be polite
                        except Exception as e:
                            self.logger.warning(f"Failed to scrape {link}: {e}")
                
            except Exception as e:
                self.logger.error(f"Playwright error for {url}: {e}")
            finally:
                await browser.close()
        
        return {
            "url": url,
            "pages_scraped": len(documents),
            "documents": documents
        }
    
    async def _extract_page_content(self, page) -> str:
        """Extract clean text content from page"""
        # Remove script and style elements
        await page.evaluate("""
            () => {
                document.querySelectorAll('script, style, nav, footer, header, aside').forEach(el => el.remove());
            }
        """)
        
        # Get text content
        content = await page.evaluate("() => document.body.innerText")
        
        # Clean up
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        return '\n'.join(lines)
    
    async def _extract_links(self, page, base_url: str, max_links: int) -> List[str]:
        """Extract relevant links from page"""
        links = await page.eval_on_selector_all("a[href]", """
            elements => elements.map(el => el.href).filter(href => 
                href && (href.includes('docs.pega.com') || 
                        href.includes('github.io') ||
                        href.includes('support.pega.com'))
            )
        """)
        
        # Remove duplicates and limit
        seen = set()
        unique_links = []
        for link in links:
            if link not in seen and link.startswith("http"):
                seen.add(link)
                unique_links.append(link)
                if len(unique_links) >= max_links:
                    break
        
        return unique_links
    
    async def documentation_search(self, query: str) -> Dict:
        """Specialized search for Pega documentation"""
        pega_query = f"{query} site:docs.pega.com OR site:community.pega.com"
        return await self.web_search(pega_query, depth=3)
    
    async def community_search(self, query: str) -> Dict:
        """Search Pega Community"""
        community_query = f"{query} site:community.pega.com upgrade issue"
        return await self.web_search(community_query, depth=2)
    
    async def scrape(self, sources: Optional[List[str]] = None,
                     force_full: bool = False) -> Dict:
        """Comprehensive scraping"""
        if sources is None:
            sources = [
                "https://docs.pega.com/bundle/customer-decision-hub/page/customer-decision-hub/update/cdh-update-intro.html",
                "https://pegasystems.github.io/pega-helm-charts/"
            ]
        
        tasks = []
        for source in sources:
            if "docs.pega.com" in source or "github.io" in source:
                # Use Playwright for deep scraping
                tasks.append(self.playwright_scrape(source, max_pages=10 if force_full else 3))
            else:
                # Use Tavily for search
                tasks.append(self.web_search(source, depth=3))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_docs = sum([
            r.get("documents", 0) if isinstance(r, dict) else 0 
            for r in results
        ])
        
        return {
            "agent": "research",
            "source": "tavily_playwright",
            "documents": total_docs,
            "details": results
        }
    
    async def _store_document(self, doc: Dict):
        """Store document in vector database"""
        chunks = self._chunk_text(doc["content"])
        metadatas = [{
            "source": doc["url"],
            "title": doc.get("title", ""),
            "category": "research",
            "chunk_index": i,
            "scraped_at": datetime.now().isoformat()
        } for i in range(len(chunks))]
        
        self.chroma.add_documents(chunks, metadatas)
    
    def _chunk_text(self, text: str, size: int = 1000, overlap: int = 200) -> List[str]:
        """Smart text chunking"""
        chunks = []
        start = 0
        while start < len(text):
            chunk = text[start:start + size]
            if len(chunk) == size:
                last_period = chunk.rfind(". ")
                if last_period > size * 0.7:
                    chunk = chunk[:last_period + 1]
                    start += last_period + 1
                else:
                    start += size - overlap
            else:
                start += size
            chunks.append(chunk.strip())
        return chunks