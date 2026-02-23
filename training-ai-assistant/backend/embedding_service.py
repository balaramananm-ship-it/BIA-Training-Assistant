"""
Embedding Service
Generates local embeddings using SentenceTransformers
"""

from typing import List
import numpy as np

class EmbeddingService:
    """Handles text embedding generation"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedding service
        
        Args:
            model_name: SentenceTransformers model to use
        """
        self.model_name = model_name
        self.model = None
        self.embedding_dim = 384  # all-MiniLM-L6-v2 dimension
    
    def _load_model(self):
        """Lazy load the model on first use"""
        if self.model is None:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Embed a single text string
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            self._load_model()
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            raise Exception(f"Error embedding text: {str(e)}")
    
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Embed multiple texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            Array of embedding vectors
        """
        try:
            self._load_model()
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings
        except Exception as e:
            raise Exception(f"Error embedding texts: {str(e)}")
    
    def similarity(self, text1: str, text2: str) -> float:
        """
        Calculate cosine similarity between two texts
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        emb1 = self.embed_text(text1)
        emb2 = self.embed_text(text2)
        
        # Cosine similarity using numpy
        dot_product = np.dot(emb1, emb2)
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        similarity = dot_product / (norm1 * norm2) if (norm1 * norm2) != 0 else 0
        return float(similarity)


# Global instance
embedding_service = EmbeddingService()
