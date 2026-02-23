"""
Quiz Generator Module
Dynamically generates MCQ quizzes from training content
"""

import json
from typing import List, Dict
from ollama_client import ollama_client
from vector_store import vector_store

class QuizGenerator:
    """Generates quizzes from training materials"""
    
    def __init__(self, temperature: float = 0.5):
        """
        Initialize quiz generator
        
        Args:
            temperature: LLM temperature for quiz generation
        """
        self.temperature = temperature
    
    def generate_quiz(self, topic: str = None, num_questions: int = 5) -> dict:
        """
        Generate a quiz on a topic or random content
        
        Args:
            topic: Optional topic to focus on
            num_questions: Number of questions to generate
            
        Returns:
            Quiz dictionary with questions and answers
        """
        try:
            # Retrieve relevant chunks
            if topic:
                query = f"Create quiz questions about: {topic}"
            else:
                query = "Generate training quiz questions"
            
            chunks = vector_store.search(query, top_k=5)
            
            if not chunks:
                return {
                    'error': True,
                    'message': 'No training materials available for quiz generation.'
                }
            
            # Build context from chunks
            context = "\n\n".join([chunk for chunk, _ in chunks])
            
            # Build prompt
            prompt = self._build_generation_prompt(context, topic, num_questions)
            
            # Generate quiz
            response = ollama_client.generate_response(
                prompt=prompt,
                temperature=self.temperature
            )
            
            # Parse response
            quiz = self._parse_quiz_response(response, num_questions)
            quiz['topic'] = topic or 'General Knowledge'
            
            return quiz
            
        except Exception as e:
            return {
                'error': True,
                'message': f'Error generating quiz: {str(e)}'
            }
    
    def _build_generation_prompt(self, context: str, topic: str, num_questions: int) -> str:
        """Build prompt for quiz generation"""
        prompt = f"""Based on the following training material, generate exactly {num_questions} multiple choice questions.

TRAINING MATERIAL:
{context[:2000]}

{"TOPIC FOCUS: " + topic if topic else ""}

Generate the quiz in the following JSON format ONLY (no other text):
{{
  "questions": [
    {{
      "id": 1,
      "question": "Question text here?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": 0,
      "explanation": "Why this answer is correct"
    }}
  ]
}}

Generate exactly {num_questions} questions. Return ONLY valid JSON."""
        
        return prompt
    
    def _parse_quiz_response(self, response: str, num_questions: int) -> dict:
        """Parse LLM response into quiz format"""
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if not json_match:
                # If parsing fails, generate a default structure
                return self._generate_default_quiz(response, num_questions)
            
            quiz_json = json.loads(json_match.group())
            
            # Validate structure
            if 'questions' not in quiz_json:
                return self._generate_default_quiz(response, num_questions)
            
            # Ensure we have the right number of questions
            questions = quiz_json['questions'][:num_questions]
            
            # Validate each question
            for q in questions:
                if 'id' not in q:
                    q['id'] = questions.index(q) + 1
                if 'options' not in q or len(q['options']) < 2:
                    q['options'] = ['Yes', 'No', 'Maybe', 'Not Sure']
                if 'correct_answer' not in q:
                    q['correct_answer'] = 0
            
            return {
                'questions': questions,
                'total_questions': len(questions),
                'error': False
            }
            
        except json.JSONDecodeError:
            return self._generate_default_quiz(response, num_questions)
    
    def _generate_default_quiz(self, text_content: str, num_questions: int) -> dict:
        """Generate a default quiz structure when parsing fails"""
        # Extract sentences as questions
        sentences = text_content.split('?')[:num_questions]
        
        questions = []
        for i, sentence in enumerate(sentences):
            question_text = sentence.strip() + "?"
            if len(question_text) > 10:
                questions.append({
                    'id': i + 1,
                    'question': question_text[:200],
                    'options': ['Yes', 'No', 'Correct', 'Incorrect'],
                    'correct_answer': 0,
                    'explanation': 'Based on training materials'
                })
        
        return {
            'questions': questions[:num_questions],
            'total_questions': len(questions[:num_questions]),
            'error': len(questions) < num_questions
        }


# Global instance
quiz_generator = QuizGenerator()
