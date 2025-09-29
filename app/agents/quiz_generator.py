from crewai import Agent, Task, Crew
from typing import Dict, Any, List
import json
import os
from dotenv import load_dotenv
from app.services.llm_service import LLMService
from app.config.crewai_config import configure_crewai_groq, get_groq_llm
from app.agents.crewai_quiz_system import CrewAIQuizSystem

load_dotenv()
configure_crewai_groq()

class QuizGeneratorAgent:
    def __init__(self, db):
        self.db = db
        self.llm_service = LLMService()
        
        # Initialize the comprehensive CrewAI system
        try:
            self.crewai_system = CrewAIQuizSystem(db)
            print("✅ CrewAI Quiz System initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize CrewAI system: {e}")
            self.crewai_system = None
        
        # Fallback: Define a simple Quiz Generation Agent using CrewAI with Groq LLM
        self.llm = get_groq_llm()
        if self.llm:
            self.quiz_agent = Agent(
                role='Educational Quiz Specialist',
                goal='Generate high-quality, educational quiz questions that test student knowledge effectively',
                backstory="""You are an expert educational content creator with deep knowledge of pedagogy, 
                assessment design, and curriculum development. You excel at creating questions that are:
                - Clear and unambiguous
                - Appropriately challenging for the difficulty level
                - Educationally valuable
                - Free from bias or trickery
                - Well-structured with logical answer options""",
                verbose=True,
                allow_delegation=False,
                llm=self.llm
            )
        else:
            self.quiz_agent = None
        
    async def generate_questions(self, quiz) -> Dict[str, Any]:
        """Generate quiz questions using CrewAI system"""
        
        try:
            print(f"🎯 QuizGenerator: Starting CrewAI question generation for quiz: {quiz['title']}")
            print(f"📚 Topic: {quiz['topic']}, Difficulty: {quiz['difficulty']}, Questions: {quiz['total_questions']}")
            
            # Use the comprehensive CrewAI system if available
            if self.crewai_system:
                print("🤖 Using comprehensive CrewAI system for quiz generation")
                return await self.crewai_system.generate_quiz_for_data(quiz)
            
            # Fallback to simple CrewAI agent if comprehensive system not available
            elif self.quiz_agent:
                print("🤖 Using fallback CrewAI agent for quiz generation")
                return await self._generate_with_simple_agent(quiz)
            
            # Final fallback to direct LLM service
            else:
                print("🤖 Using direct LLM service as final fallback")
                return await self._generate_with_direct_llm(quiz)
                
        except Exception as e:
            print(f"❌ QuizGenerator: Error in quiz generation: {str(e)}")
            return {
                "success": False,
                "message": f"Quiz generation failed: {str(e)}",
                "error": str(e)
            }
    
    async def _generate_with_simple_agent(self, quiz) -> Dict[str, Any]:
        """Generate questions using simple CrewAI agent"""
        
        try:
            # Create a CrewAI Task for quiz generation
            quiz_task = Task(
                description=f"""
                Generate {quiz['total_questions']} high-quality multiple choice questions about {quiz['topic']} 
                with {quiz['difficulty']} difficulty level.
                
                Requirements:
                1. Each question must have exactly 4 options (A, B, C, D)
                2. Only one correct answer per question
                3. Questions should be clear, unambiguous, and educationally valuable
                4. Difficulty should match the specified level: {quiz['difficulty']}
                5. Questions should be relevant to the topic: {quiz['topic']}
                6. Include a mix of factual and conceptual questions
                7. Provide clear explanations for correct answers
                
                Return the questions in this exact JSON format:
                {{
                    "questions": [
                        {{
                            "question_text": "Question text here",
                            "options": ["Option A", "Option B", "Option C", "Option D"],
                            "correct_answer": "Option A",
                            "explanation": "Brief explanation of the correct answer"
                        }}
                    ]
                }}
                """,
                agent=self.quiz_agent,
                expected_output="JSON object with questions array containing question_text, options, correct_answer, and explanation for each question"
            )
            
            # Create and execute the CrewAI crew
            crew = Crew(
                agents=[self.quiz_agent],
                tasks=[quiz_task],
                verbose=True
            )
            
            print("🤖 Executing CrewAI quiz generation...")
            result = crew.kickoff()
            
            # Parse the result
            questions_data = json.loads(str(result))
            questions = questions_data.get('questions', [])
            
            print(f"📝 Generated {len(questions)} questions using CrewAI agent")
            
            # Validate and save questions
            return await self._validate_and_save_questions(questions, quiz)
            
        except Exception as e:
            print(f"❌ Simple CrewAI agent failed: {str(e)}")
            return {
                "success": False,
                "message": f"CrewAI agent failed: {str(e)}",
                "error": str(e)
            }
    
    async def _generate_with_direct_llm(self, quiz) -> Dict[str, Any]:
        """Generate questions using direct LLM service"""
        
        try:
            print("🤖 Using direct LLM service for quiz generation")
            
            questions_data = await self.llm_service.generate_quiz_questions(
                topic=quiz['topic'],
                difficulty=quiz['difficulty'],
                num_questions=quiz['total_questions']
            )
            
            questions = questions_data.get('questions', [])
            print(f"📝 Generated {len(questions)} questions using direct LLM")
            
            # Validate and save questions
            return await self._validate_and_save_questions(questions, quiz)
            
        except Exception as e:
            print(f"❌ Direct LLM service failed: {str(e)}")
            return {
                "success": False,
                "message": f"Direct LLM service failed: {str(e)}",
                "error": str(e)
            }
    
    async def _validate_and_save_questions(self, questions: List[Dict], quiz: Dict) -> Dict[str, Any]:
        """Validate questions and save to database"""
        
        try:
            # Validate questions before saving
            if not questions:
                print("❌ No questions received")
                return {
                    "success": False,
                    "message": "No questions generated",
                    "error": "Empty questions array"
                }
            
            # Validate question structure
            for i, question in enumerate(questions):
                if not question.get('question_text') or not question.get('options') or not question.get('correct_answer'):
                    print(f"❌ Invalid question structure at index {i}: {question}")
                    return {
                        "success": False,
                        "message": "Invalid question structure",
                        "error": f"Question {i+1} missing required fields"
                    }
            
            print("✅ Generated valid questions - proceeding to save to database")
            
            # Save questions to database
            from app.services.firebase_service import FirebaseService
            firebase_service = FirebaseService(self.db)
            
            saved_questions = []
            for i, question_data in enumerate(questions):
                print(f"💾 Saving question {i+1}: {question_data.get('question_text', 'No text')[:50]}...")
                
                question_dict = {
                    "quiz_id": quiz['id'],
                    "question_text": question_data['question_text'],
                    "options": question_data['options'],
                    "correct_answer": question_data['correct_answer'],
                    "time_limit": quiz['time_per_question'],
                    "order": i + 1
                }
                
                try:
                    question = await firebase_service.create_question(question_dict)
                    saved_questions.append(question)
                    print(f"✅ Question {i+1} saved successfully")
                except Exception as e:
                    print(f"❌ Failed to save question {i+1}: {e}")
                    # If any question fails to save, rollback all saved questions
                    print("🔄 Rolling back saved questions due to save failure")
                    for saved_question in saved_questions:
                        try:
                            # Delete the saved question
                            firebase_service.db.collection('questions').document(saved_question['id']).delete()
                            print(f"🗑️ Deleted question {saved_question['id']}")
                        except Exception as delete_error:
                            print(f"❌ Failed to delete question {saved_question['id']}: {delete_error}")
                    
                    return {
                        "success": False,
                        "message": f"Failed to save questions to database: {str(e)}",
                        "error": str(e)
                    }
            
            print(f"✅ Successfully saved {len(saved_questions)} questions to database")
            
            return {
                "success": True,
                "message": f"Generated {len(saved_questions)} questions successfully",
                "questions_count": len(saved_questions),
                "quiz_id": quiz['id']
            }
            
        except Exception as e:
            print(f"❌ Error validating and saving questions: {str(e)}")
            return {
                "success": False,
                "message": f"Error saving questions: {str(e)}",
                "error": str(e)
            }
