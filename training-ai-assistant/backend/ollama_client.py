"""
Ollama Integration Module
Handles local LLM inference using llama3.2 via Ollama
"""

import requests
import json
from typing import Generator
import os

OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")
MODEL_NAME = os.getenv("MODEL_NAME", "llama3.2")

class OllamaClient:
    """Wrapper for Ollama API interactions"""
    
    def __init__(self, api_url: str = OLLAMA_API_URL, model: str = MODEL_NAME):
        self.api_url = api_url
        self.model = model
    
    def generate_response(self, prompt: str, context: str = "", temperature: float = 0.7) -> str:
        """
        Generate a response using llama3.2 via Ollama
        
        Args:
            prompt: The input prompt
            context: Optional context to prepend
            temperature: Sampling temperature (0-1)
        
        Returns:
            Generated response text
        """
        full_prompt = f"{context}\n{prompt}" if context else prompt
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "temperature": temperature,
            "stream": False
        }
        
        try:
            response = requests.post(self.api_url, json=payload, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "").strip()
        
        except requests.exceptions.ConnectionError:
            raise Exception(f"Failed to connect to Ollama at {self.api_url}. Is Ollama running?")
        except requests.exceptions.Timeout:
            raise Exception("Ollama request timed out. The model may be too slow.")
        except Exception as e:
            raise Exception(f"Ollama API error: {str(e)}")
    
    def generate_response_stream(self, prompt: str, context: str = "", temperature: float = 0.7) -> Generator[str, None, None]:
        """
        Generate a response with streaming
        
        Args:
            prompt: The input prompt
            context: Optional context to prepend
            temperature: Sampling temperature (0-1)
        
        Yields:
            Response chunks
        """
        full_prompt = f"{context}\n{prompt}" if context else prompt
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "temperature": temperature,
            "stream": True
        }
        
        try:
            response = requests.post(self.api_url, json=payload, stream=True, timeout=120)
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    token = chunk.get("response", "")
                    if token:
                        yield token
        
        except Exception as e:
            raise Exception(f"Ollama streaming error: {str(e)}")
    
    def health_check(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            response = requests.get(self.api_url.replace("/api/generate", "/api/tags"), timeout=5)
            return response.status_code == 200
        except:
            return False


# Global instance
ollama_client = OllamaClient()
