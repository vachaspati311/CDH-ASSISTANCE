class SearchTools:
    def __init__(self, chroma_manager):
        self.chroma = chroma_manager
    
    def search_docs(self, query, n_results=5):
        return self.chroma.search(query, n_results=n_results)
    
    def search_by_category(self, query, category, n_results=5):
        return self.chroma.search(query, n_results=n_results, filter_dict={"category": category})
