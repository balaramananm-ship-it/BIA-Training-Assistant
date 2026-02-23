"""
Vector Store Module
FAISS-based vector database for semantic search
"""

import faiss
import numpy as np
import pickle
import os
from typing import List, Tuple
from embedding_service import embedding_service

class VectorStore:
    """FAISS-based vector store for document chunks"""
    
    def __init__(self, vectorstore_path: str = "vectorstore/index.faiss"):
        """
        Initialize vector store
        
        Args:
            vectorstore_path: Path to store FAISS index
        """
        self.vectorstore_path = vectorstore_path
        self.index = None
        self.chunks = []
        self.embeddings = None
        self.metadata = []
        
        os.makedirs(os.path.dirname(vectorstore_path), exist_ok=True)
        self._load_or_create_index()
    
    def _load_or_create_index(self):
        """Load existing index or create new one"""
        if os.path.exists(self.vectorstore_path):
            try:
                self.index = faiss.read_index(self.vectorstore_path)
                # Load metadata
                metadata_path = self.vectorstore_path.replace('.faiss', '_metadata.pkl')
                if os.path.exists(metadata_path):
                    with open(metadata_path, 'rb') as f:
                        self.chunks, self.metadata = pickle.load(f)
            except Exception as e:
                print(f"Error loading index: {e}, creating new index")
                self._create_new_index()
        else:
            self._create_new_index()
    
    def _create_new_index(self):
        """Create a new FAISS index"""
        embedding_dim = embedding_service.embedding_dim
        self.index = faiss.IndexFlatL2(embedding_dim)
        self.chunks = []
        self.metadata = []
    
    def add_chunks(self, chunks: List[str], document_name: str = "unknown"):
        """
        Add document chunks to the vector store
        
        Args:
            chunks: List of text chunks
            document_name: Name of source document
        """
        if not chunks:
            return
        
        try:
            # Generate embeddings
            embeddings = embedding_service.embed_texts(chunks)
            
            # Add to FAISS index
            if self.index is None:
                self._create_new_index()
            
            embeddings = embeddings.astype(np.float32)
            self.index.add(embeddings)
            
            # Store chunks and metadata
            for chunk in chunks:
                self.chunks.append(chunk)
                self.metadata.append({
                    'text': chunk,
                    'document': document_name,
                    'length': len(chunk)
                })
            
            self._save_index()
            
        except Exception as e:
            raise Exception(f"Error adding chunks to vector store: {str(e)}")
    
    def search(self, query: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """
        Search for relevant chunks
        
        Args:
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            List of (chunk_text, score) tuples
        """
        if self.index is None or len(self.chunks) == 0:
            return []
        
        try:
            # Embed query
            query_embedding = embedding_service.embed_text(query)
            query_embedding = np.array([query_embedding], dtype=np.float32)
            
            # Search
            distances, indices = self.index.search(query_embedding, min(top_k, len(self.chunks)))
            
            results = []
            for i, idx in enumerate(indices[0]):
                if idx >= 0 and idx < len(self.chunks):
                    chunk = self.chunks[idx]
                    distance = distances[0][i]
                    # Convert L2 distance to similarity score (0-1)
                    similarity = 1.0 / (1.0 + distance)
                    results.append((chunk, similarity))
            
            return results
            
        except Exception as e:
            raise Exception(f"Error searching vector store: {str(e)}")
    
    def _save_index(self):
        """Save FAISS index to disk"""
        try:
            os.makedirs(os.path.dirname(self.vectorstore_path), exist_ok=True)
            faiss.write_index(self.index, self.vectorstore_path)
            
            # Save metadata
            metadata_path = self.vectorstore_path.replace('.faiss', '_metadata.pkl')
            with open(metadata_path, 'wb') as f:
                pickle.dump((self.chunks, self.metadata), f)
        except Exception as e:
            print(f"Error saving index: {e}")
    
    def get_stats(self) -> dict:
        """Get vector store statistics"""
        return {
            'total_chunks': len(self.chunks),
            'total_documents': len(set(m['document'] for m in self.metadata)),
            'index_size': self.index.ntotal if self.index else 0,
            'embedding_dimension': embedding_service.embedding_dim
        }
    
    def clear(self):
        """Clear the vector store"""
        self.index = None
        self.chunks = []
        self.metadata = []
        self._create_new_index()
        # Remove files
        if os.path.exists(self.vectorstore_path):
            os.remove(self.vectorstore_path)
        metadata_path = self.vectorstore_path.replace('.faiss', '_metadata.pkl')
        if os.path.exists(metadata_path):
            os.remove(metadata_path)


# Global instance
vector_store = VectorStore()
