from typing import List, Dict, Any

class SimpleRetriever:
    def __init__(self, chroma_manager):
        self.chroma = chroma_manager
    
    def retrieve(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        return self.chroma.search(query, n_results=k)
    
    def retrieve_with_filter(self, query: str, filter_dict: dict, k: int = 5):
        return self.chroma.search(query, n_results=k, filter_dict=filter_dict)
