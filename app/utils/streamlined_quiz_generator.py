"""
Streamlined Quiz Generator - Single tool for quiz generation with minimal prompts
"""

import asyncio
import json
from typing import Dict, Any, List
from app.config.crewai_config import get_crewai_llm
from app.utils.rate_limiter import execute_with_rate_limit
from app.utils.fallback_system import fallback_system
from crewai import Agent, Task, Crew

class StreamlinedQuizGenerator:
    def __init__(self, db):
        self.db = db
        self.llm = get_crewai_llm()
        
        if not self.llm:
            raise ValueError("Failed to initialize CrewAI LLM")
        
        # Single optimized agent for quiz generation
        self.quiz_agent = Agent(
            role='Quiz Generator',
            goal='Generate quiz questions efficiently',
            backstory='Expert at creating educational quiz questions',
            verbose=False,
            allow_delegation=False,
            llm=self.llm
        )
    
    async def generate_quiz(self, topic: str, difficulty: str = "medium", num_questions: int = 5) -> Dict[str, Any]:
        """
        Generate quiz questions with minimal prompts and maximum efficiency
        
        Args:
            topic: Quiz topic
            difficulty: easy|medium|hard
            num_questions: Number of questions to generate
            
        Returns:
            Dict with success status and questions
        """
        try:
            print(f"🎯 Generating {num_questions} {difficulty} questions about {topic}")
            
            # Minimal prompt for maximum efficiency
            task = Task(
                description=f"""Create {num_questions} {difficulty} quiz questions about {topic}.

Format: {{"questions": [{{"question_text": "...", "options": ["A", "B", "C", "D"], "correct_answer": "A", "explanation": "..."}}]}}""",
                agent=self.quiz_agent,
                expected_output="JSON with questions array"
            )
            
            # Execute with rate limiting
            async def _execute_quiz():
                crew = Crew(
                    agents=[self.quiz_agent],
                    tasks=[task],
                    verbose=False
                )
                return crew.kickoff()
            
            try:
                result = await execute_with_rate_limit(
                    _execute_quiz,
                    estimated_tokens=800  # Reduced token estimate
                )
                
                # Parse result
                questions_data = self._parse_result(result)
                questions = questions_data.get('questions', [])
                
                if questions:
                    return {
                        "success": True,
                        "message": f"Generated {len(questions)} questions",
                        "questions": questions,
                        "system_used": "Streamlined CrewAI"
                    }
                else:
                    raise Exception("No questions generated")
                    
            except Exception as e:
                if "rate_limit" in str(e).lower():
                    print("⚠️ Rate limit hit, using fallback system")
                    return await fallback_system.generate_fallback_questions(
                        topic=topic,
                        difficulty=difficulty,
                        num_questions=num_questions
                    )
                else:
                    raise
                    
        except Exception as e:
            print(f"❌ Quiz generation failed: {str(e)}")
            return {
                "success": False,
                "message": f"Quiz generation failed: {str(e)}",
                "error": str(e)
            }
    
    def _parse_result(self, result) -> Dict[str, Any]:
        """Parse CrewAI result with minimal processing"""
        try:
            result_str = str(result)
            
            # Clean result
            cleaned = result_str.strip()
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            if cleaned.startswith('```'):
                cleaned = cleaned[3:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            
            cleaned = cleaned.strip()
            
            # Try to parse JSON
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                # Extract JSON from content
                import re
                json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                else:
                    raise Exception("No valid JSON found in result")
                    
        except Exception as e:
            print(f"❌ Result parsing failed: {str(e)}")
            # Return fallback structure
            return {
                "questions": [
                    {
                        "question_text": f"What is a key concept in {topic}?",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correct_answer": "Option A",
                        "explanation": f"This is a basic question about {topic}"
                    }
                ]
            }

# Global instance
quiz_generator = None

def get_quiz_generator(db):
    """Get or create quiz generator instance"""
    global quiz_generator
    if quiz_generator is None:
        quiz_generator = StreamlinedQuizGenerator(db)
    return quiz_generator
