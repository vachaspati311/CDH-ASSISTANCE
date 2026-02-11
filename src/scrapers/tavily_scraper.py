import os
from tavily import TavilyClient

class TavilyScraper:
    def __init__(self):
        self.client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    
    def search(self, query, max_results=10, search_depth="advanced"):
        try:
            response = self.client.search(
                query=query,
                max_results=max_results,
                search_depth=search_depth,
                include_answer=True,
                include_raw_content=True
            )
            return response
        except Exception as e:
            return {"error": str(e), "results": []}
    
    def search_pega_docs(self, query):
        pega_query = f"{query} site:docs.pega.com"
        return self.search(pega_query, max_results=5)
