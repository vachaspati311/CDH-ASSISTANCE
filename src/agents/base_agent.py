# src/agents/base_agent.py - Updated for M4 16GB

import os
import logging
from abc import ABC
from typing import Dict, List, Any, Optional

import ollama

class BaseAgent(ABC):
    """Base agent optimized for M4 16GB MacBook"""
    
    def __init__(self, chroma_manager):
        self.chroma = chroma_manager
        self.logger = logging.getLogger(self.__class__.__name__)
        self.description = "Base agent"
        self.capabilities: List[str] = []
        
        self.ollama_client = ollama.Client(
            host=os.getenv("OLLAMA_HOST", "http://localhost:11434")
        )
        
        # M4 16GB: Use 8B model by default
        self.default_model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
        
        # Model selection based on task
        self.models = {
            "general": "llama3.1:8b",      # ~5GB RAM, good for most tasks
            "coding": "codellama:7b",      # Code-specific
            "analysis": "mistral:7b",      # Analytical tasks
            "fast": "llama3.1:8b"          # Quick responses
        }
    
    def _get_env(self, key: str) -> str:
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Environment variable {key} not set")
        return value
    
    async def _call_ollama(self, prompt: str, model: Optional[str] = None, 
                          task_type: str = "general") -> str:
        """
        Call Ollama with M4 16GB optimizations
        
        Args:
            prompt: The prompt text
            model: Specific model to use (optional)
            task_type: Type of task for auto model selection
        """
        # Auto-select model based on task
        selected_model = model or self.models.get(task_type, self.default_model)
        
        # M4 16GB optimizations
        options = {
            "temperature": 0.1,
            "num_predict": 2048,        # Limit tokens for speed
            "top_p": 0.9,
            "repeat_penalty": 1.1,
            # M4 specific optimizations
            "num_ctx": 4096,            # Context window (reduced for 8B)
            "num_thread": 8,            # M4 has 10 cores, use 8 for LLM
            "num_gpu": 1,               # Use M4 GPU
        }
        
        try:
            self.logger.info(f"Calling Ollama: {selected_model} (M4 16GB optimized)")
            
            response = self.ollama_client.generate(
                model=selected_model,
                prompt=prompt,
                options=options
            )
            
            return response['response']
            
        except Exception as e:
            self.logger.error(f"Ollama error with {selected_model}: {e}")
            
            # Fallback to smaller model if OOM
            if "out of memory" in str(e).lower():
                self.logger.warning("OOM detected, falling back to smaller context")
                options["num_ctx"] = 2048
                options["num_predict"] = 1024
                
                response = self.ollama_client.generate(
                    model="llama3.1:8b",  # Force 8B
                    prompt=prompt[:4000],  # Truncate prompt
                    options=options
                )
                return response['response']
            
            return f"Error: {e}"
    
    async def _call_ollama_stream(self, prompt: str, task_type: str = "general"):
        """Stream responses for better UX on M4"""
        selected_model = self.models.get(task_type, self.default_model)
        
        stream = self.ollama_client.generate(
            model=selected_model,
            prompt=prompt,
            options={
                "temperature": 0.1,
                "num_predict": 2048,
                "num_ctx": 4096,
                "num_thread": 8,
            },
            stream=True
        )
        
        for chunk in stream:
            yield chunk['response']