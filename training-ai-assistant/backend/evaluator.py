"""
Evaluator Module
Evaluates employee answers using LLM
"""

import json
from typing import Dict, List
from ollama_client import ollama_client

class Evaluator:
    """Evaluates quiz answers and provides feedback"""
    
    def __init__(self, temperature: float = 0.2):
        """
        Initialize evaluator
        
        Args:
            temperature: LLM temperature (lower = more consistent scoring)
        """
        self.temperature = temperature
    
    def evaluate_answer(self, question: str, correct_answer: str, 
                       user_answer: str, options: List[str] = None) -> dict:
        """
        Evaluate a single answer
        
        Args:
            question: The quiz question
            correct_answer: The correct answer text or index
            user_answer: The employee's answer
            options: Multiple choice options (if applicable)
            
        Returns:
            Dict with score, feedback, and analysis
        """
        try:
            # For MCQ with index
            if isinstance(correct_answer, int) and options:
                correct_text = options[correct_answer]
                is_correct = user_answer.lower().strip() == correct_text.lower().strip()
            else:
                # For free-form answers, use LLM evaluation
                is_correct = self._evaluate_semantic_match(question, correct_answer, user_answer)
            
            if is_correct:
                score = 1.0
                feedback = "Correct! Well done."
            else:
                score = 0.0
                feedback = self._generate_feedback(question, correct_answer, user_answer)
            
            return {
                'score': score,
                'feedback': feedback,
                'is_correct': is_correct,
                'question': question,
                'correct_answer': correct_answer,
                'user_answer': user_answer
            }
            
        except Exception as e:
            return {
                'score': 0.0,
                'feedback': f'Error evaluating answer: {str(e)}',
                'is_correct': False,
                'question': question,
                'error': True
            }
    
    def evaluate_quiz(self, quiz_responses: List[Dict]) -> dict:
        """
        Evaluate multiple quiz answers
        
        Args:
            quiz_responses: List of {'question_id': int, 'answer': str, 'correct': str}
            
        Returns:
            Aggregated results and feedback
        """
        results = []
        total_score = 0.0
        
        for response in quiz_responses:
            evaluation = self.evaluate_answer(
                question=response.get('question', ''),
                correct_answer=response.get('correct', ''),
                user_answer=response.get('answer', ''),
                options=response.get('options', None)
            )
            results.append(evaluation)
            total_score += evaluation['score']
        
        num_questions = len(quiz_responses)
        percentage = (total_score / num_questions * 100) if num_questions > 0 else 0
        
        # Generate overall feedback
        overall_feedback = self._generate_overall_feedback(percentage, results)
        
        return {
            'total_questions': num_questions,
            'correct_answers': int(total_score),
            'percentage': round(percentage, 1),
            'overall_feedback': overall_feedback,
            'detailed_results': results
        }
    
    def _evaluate_semantic_match(self, question: str, expected: str, actual: str) -> bool:
        """
        Use LLM to evaluate semantic match for free-form answers
        """
        prompt = f"""Compare these two answers to determine if they're semantically equivalent:

QUESTION: {question}

EXPECTED ANSWER: {expected}

ACTUAL ANSWER: {actual}

Are these answers essentially saying the same thing? Respond with ONLY "YES" or "NO"."""
        
        try:
            response = ollama_client.generate_response(
                prompt=prompt,
                temperature=self.temperature
            )
            return response.strip().upper() == "YES"
        except:
            return False
    
    def _generate_feedback(self, question: str, correct: str, actual: str) -> str:
        """Generate personalized feedback on incorrect answer"""
        prompt = f"""Provide brief, encouraging feedback on this quiz answer (2-3 sentences max):

QUESTION: {question}

CORRECT ANSWER: {correct}

STUDENT'S ANSWER: {actual}

Feedback:"""
        
        try:
            feedback = ollama_client.generate_response(
                prompt=prompt,
                temperature=self.temperature
            )
            return feedback.strip()[:300]
        except:
            return "Incorrect. Please review the training materials for more information."
    
    def _generate_overall_feedback(self, percentage: float, results: List[Dict]) -> str:
        """Generate overall quiz feedback based on performance"""
        if percentage >= 80:
            feedback = "Excellent work! You have a strong understanding of the material."
        elif percentage >= 60:
            feedback = "Good effort! Review the materials for topics you found challenging."
        elif percentage >= 40:
            feedback = "You're making progress. Consider reviewing the training materials more carefully."
        else:
            feedback = "You may need to spend more time with the training materials. Don't hesitate to ask for help!"
        
        return feedback


# Global instance
evaluator = Evaluator()
