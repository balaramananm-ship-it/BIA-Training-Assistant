"""
RAG (Retrieval Augmented Generation) Pipeline
Combines vector retrieval with LLM generation
"""

from typing import List, Tuple
from ollama_client import ollama_client
from vector_store import vector_store

class RAGPipeline:
    """Handles RAG workflow for grounded QA"""
    
    def __init__(self, top_k: int = 3, temperature: float = 0.3):
        """
        Initialize RAG pipeline
        
        Args:
            top_k: Number of chunks to retrieve
            temperature: LLM temperature (lower = more factual)
        """
        self.top_k = top_k
        self.temperature = temperature
    
    def _build_context(self, chunks: List[Tuple[str, float]]) -> str:
        """Build context string from retrieved chunks"""
        context_parts = []
        for chunk, score in chunks:
            context_parts.append(f"[Relevance: {score:.2%}]\n{chunk}\n")
        
        return "\n---\n".join(context_parts)
    
    def _build_prompt(self, question: str, context: str) -> str:
        """Build the final prompt for the LLM"""
        system_message = """You are a helpful employee onboarding assistant. 
Answer questions based ONLY on the provided company training materials.
If the answer cannot be found in the materials, say "I don't have that information in the training materials."
Be concise, clear, and professional."""
        
        prompt = f"""{system_message}

TRAINING MATERIALS:
{context}

QUESTION: {question}

ANSWER:"""
        
        return prompt
    
    def answer_question(self, question: str) -> dict:
        """
        Answer a question using RAG pipeline
        
        Args:
            question: User question
            
        Returns:
            Dict with answer, sources, and metadata
        """
        try:
            # Retrieve relevant chunks
            chunks = vector_store.search(question, self.top_k)
            
            if not chunks:
                return {
                    'answer': 'No relevant training materials found. Please upload documents to get started.',
                    'sources': [],
                    'confidence': 0.0,
                    'question': question
                }
            
            # Build context
            context = self._build_context(chunks)
            
            # Build prompt
            prompt = self._build_prompt(question, context)
            
            # Generate response
            response = ollama_client.generate_response(
                prompt=prompt,
                temperature=self.temperature
            )
            
            # Extract sources
            sources = [chunk for chunk, _ in chunks]
            
            # Calculate confidence (average of retrieval scores)
            confidence = float(sum(score for _, score in chunks) / len(chunks))
            
            return {
                'answer': response,
                'sources': sources,
                'confidence': confidence,
                'question': question
            }
            
        except Exception as e:
            return {
                'answer': f"Error processing question: {str(e)}",
                'sources': [],
                'confidence': 0.0,
                'question': question,
                'error': True
            }
    
    def answer_question_stream(self, question: str):
        """
        Answer a question with streaming response
        
        Args:
            question: User question
            
        Yields:
            Response tokens
        """
        try:
            # Retrieve relevant chunks
            chunks = vector_store.search(question, self.top_k)
            
            if not chunks:
                yield "No relevant training materials found. Please upload documents to get started."
                return
            
            # Build context
            context = self._build_context(chunks)
            
            # Build prompt
            prompt = self._build_prompt(question, context)
            
            # Generate response stream
            for token in ollama_client.generate_response_stream(
                prompt=prompt,
                temperature=self.temperature
            ):
                yield token
            
        except Exception as e:
            yield f"Error processing question: {str(e)}"


# Global instance
rag_pipeline = RAGPipeline()
