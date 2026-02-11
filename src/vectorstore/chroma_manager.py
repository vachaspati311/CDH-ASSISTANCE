# src/vectorstore/chroma_manager.py
import os
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

import chromadb
from chromadb.config import Settings
from openai import OpenAI

@dataclass
class SearchResult:
    content: str
    metadata: Dict[str, Any]
    distance: float
    relevance_score: float

class ChromaManager:
    """ChromaDB with OpenAI embeddings"""
    
    def __init__(self):
        self.host = os.getenv("CHROMA_HOST", "localhost")
        self.port = int(os.getenv("CHROMA_PORT", "8000"))
        
        self.openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")
        
        self.client = chromadb.HttpClient(
            host=self.host,
            port=self.port,
            settings=Settings(anonymized_telemetry=False)
        )
        
        self.collection = self.client.get_or_create_collection(
            name="pega_knowledge",
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_documents(self, texts: List[str], metadatas: List[Dict]) -> int:
        """Add documents with OpenAI embeddings"""
        if not texts:
            return 0
        
        embeddings = self._generate_embeddings(texts)
        
        ids = [hash(f"{meta.get('source', '')}_{i}") for i, meta in enumerate(metadatas)]
        
        self.collection.add(
            ids=[str(i) for i in ids],
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings
        )
        
        return len(texts)
    
    def search(self, query: str, n_results: int = 5,
               filter_dict: Optional[Dict] = None) -> List[SearchResult]:
        """Search using OpenAI embeddings"""
        query_embedding = self._generate_embeddings([query])[0]
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_dict,
            include=["documents", "metadatas", "distances"]
        )
        
        search_results = []
        for i in range(len(results['ids'][0])):
            distance = results['distances'][0][i]
            search_results.append(SearchResult(
                content=results['documents'][0][i],
                metadata=results['metadatas'][0][i],
                distance=distance,
                relevance_score=1 - distance
            ))
        
        return search_results
    
    def get_stats(self) -> Dict:
        return {
            "total_documents": self.collection.count(),
            "embedding_model": self.embedding_model
        }
    
    def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings with OpenAI"""
        batch_size = 100
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            response = self.openai.embeddings.create(
                model=self.embedding_model,
                input=batch
            )
            
            batch_embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(batch_embeddings)
        
        return all_embeddings