"""
Fallback system for when rate limits are reached
"""

import asyncio
import json
from typing import Dict, Any, List
from app.services.llm_service import LLMService

class FallbackQuizSystem:
    def __init__(self):
        self.llm_service = LLMService()
        
    async def generate_fallback_questions(self, topic: str, difficulty: str, num_questions: int) -> Dict[str, Any]:
        """
        Generate fallback questions when CrewAI system hits rate limits
        """
        try:
            print(f"🔄 Using fallback system for {topic} quiz")
            
            # Use direct LLM service with optimized prompts
            questions_data = await self.llm_service.generate_quiz_questions(
                topic=topic,
                difficulty=difficulty,
                num_questions=num_questions
            )
            
            return {
                "success": True,
                "message": f"Generated {num_questions} questions using fallback system",
                "questions": questions_data.get('questions', []),
                "system_used": "Fallback LLM System"
            }
            
        except Exception as e:
            print(f"❌ Fallback system also failed: {str(e)}")
            return self._generate_static_questions(topic, difficulty, num_questions)
    
    def _generate_static_questions(self, topic: str, difficulty: str, num_questions: int) -> Dict[str, Any]:
        """
        Generate static questions as last resort
        """
        print(f"📚 Using static question bank for {topic}")
        
        # Static question templates
        static_questions = {
            "python": [
                {
                    "question_text": "What is the correct syntax to create a list in Python?",
                    "options": ["list()", "[]", "new list()", "List()"],
                    "correct_answer": "[]",
                    "explanation": "In Python, lists are created using square brackets []"
                },
                {
                    "question_text": "Which keyword is used to define a function in Python?",
                    "options": ["function", "def", "func", "define"],
                    "correct_answer": "def",
                    "explanation": "The 'def' keyword is used to define functions in Python"
                }
            ],
            "machine learning": [
                {
                    "question_text": "What is supervised learning?",
                    "options": [
                        "Learning without labels",
                        "Learning with labeled data",
                        "Learning from rewards",
                        "Learning without data"
                    ],
                    "correct_answer": "Learning with labeled data",
                    "explanation": "Supervised learning uses labeled training data to learn patterns"
                },
                {
                    "question_text": "What is the purpose of training data in machine learning?",
                    "options": [
                        "To test the model",
                        "To train the model",
                        "To validate the model",
                        "To deploy the model"
                    ],
                    "correct_answer": "To train the model",
                    "explanation": "Training data is used to teach the model patterns and relationships"
                }
            ],
            "data structures": [
                {
                    "question_text": "What is the time complexity of accessing an element in an array?",
                    "options": ["O(n)", "O(log n)", "O(1)", "O(n²)"],
                    "correct_answer": "O(1)",
                    "explanation": "Array access is constant time O(1) using index"
                },
                {
                    "question_text": "Which data structure follows LIFO principle?",
                    "options": ["Queue", "Stack", "Array", "Linked List"],
                    "correct_answer": "Stack",
                    "explanation": "Stack follows Last In, First Out (LIFO) principle"
                }
            ]
        }
        
        # Get questions for the topic
        topic_key = topic.lower().replace(" ", "_")
        if topic_key in static_questions:
            questions = static_questions[topic_key][:num_questions]
        else:
            # Generic questions
            questions = [
                {
                    "question_text": f"What is a key concept in {topic}?",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": "Option A",
                    "explanation": f"This is a basic question about {topic}"
                }
            ]
        
        return {
            "success": True,
            "message": f"Generated {len(questions)} static questions for {topic}",
            "questions": questions,
            "system_used": "Static Question Bank"
        }

# Global fallback system
fallback_system = FallbackQuizSystem()
