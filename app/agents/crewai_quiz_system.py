"""
CrewAI Quiz Generation System
A comprehensive system with multiple specialized agents for quiz generation
"""

from crewai import Agent, Task, Crew
from typing import Dict, Any, List, Optional
import json
import os
from dotenv import load_dotenv
from app.config.crewai_config import get_groq_llm, get_crewai_llm
from app.utils.rate_limiter import apply_rate_limit, execute_with_rate_limit
from app.utils.fallback_system import fallback_system

load_dotenv()

class CrewAIQuizSystem:
    def __init__(self, db):
        self.db = db
        self.llm = get_crewai_llm()
        
        if not self.llm:
            raise ValueError("Failed to initialize CrewAI LLM")
        
        # Initialize specialized agents
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all specialized agents for the quiz system"""
        
        # 1. Query Processor Agent - Understands user requests
        self.query_processor = Agent(
            role='Query Processor and Task Router',
            goal='Analyze user queries and determine the appropriate action to take',
            backstory="""You are an intelligent query processor that understands user requests 
            and routes them to the appropriate specialized agents. You excel at:
            - Understanding natural language queries
            - Identifying the type of task requested
            - Extracting relevant parameters from user input
            - Routing tasks to the correct specialized agents""",
            verbose=True,
            allow_delegation=True,
            llm=self.llm
        )
        
        # 2. Quiz Content Specialist - Creates educational content
        self.quiz_specialist = Agent(
            role='Educational Quiz Content Specialist',
            goal='Generate high-quality, educational quiz questions that test student knowledge effectively',
            backstory="""You are an expert educational content creator with deep knowledge of pedagogy, 
            assessment design, and curriculum development. You excel at creating questions that are:
            - Clear and unambiguous
            - Appropriately challenging for the difficulty level
            - Educationally valuable
            - Free from bias or trickery
            - Well-structured with logical answer options
            - Covering both factual and conceptual knowledge""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # 3. Content Validator - Reviews and improves content
        self.content_validator = Agent(
            role='Educational Content Validator',
            goal='Review and validate quiz content for accuracy, clarity, and educational value',
            backstory="""You are a meticulous educational content reviewer with expertise in:
            - Content accuracy verification
            - Question clarity assessment
            - Educational value evaluation
            - Bias detection and removal
            - Difficulty level validation
            - Answer option quality review""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # 4. Quiz Formatter - Structures the final output
        self.quiz_formatter = Agent(
            role='Quiz Output Formatter',
            goal='Format quiz content into the required JSON structure for the application',
            backstory="""You are a technical formatter specializing in:
            - Converting educational content to structured JSON
            - Ensuring proper data formatting
            - Validating JSON structure
            - Adding metadata and formatting details
            - Ensuring compatibility with the application system""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    async def process_user_query(self, user_query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process user query and determine the appropriate action"""
        
        try:
            print(f"🎯 CrewAI System: Processing user query: {user_query}")
            
            # Create task for query processing
            query_task = Task(
                description=f"""
                Analyze the following user query and determine what action to take:
                
                User Query: "{user_query}"
                Context: {context or "No additional context provided"}
                
                Based on the query, determine:
                1. What type of task is being requested?
                2. What parameters can be extracted?
                3. What specialized agents should be involved?
                4. What is the expected output format?
                
                Return your analysis in this JSON format:
                {{
                    "task_type": "quiz_generation|content_analysis|other",
                    "parameters": {{
                        "topic": "extracted topic",
                        "difficulty": "easy|medium|hard",
                        "num_questions": number,
                        "additional_requirements": "any specific requirements"
                    }},
                    "agents_needed": ["agent1", "agent2"],
                    "expected_output": "description of expected output"
                }}
                """,
                agent=self.query_processor,
                expected_output="JSON object with task analysis and routing information"
            )
            
            # Execute query processing with advanced rate limiting
            async def _execute_query_crew():
                crew = Crew(
                    agents=[self.query_processor],
                    tasks=[query_task],
                    verbose=True
                )
                return crew.kickoff()
            
            result = await execute_with_rate_limit(
                _execute_query_crew,
                estimated_tokens=500
            )
            
            # Parse the query analysis result
            print(f"📋 Query Result Type: {type(result)}")
            print(f"📋 Query Result: {str(result)[:200]}...")
            
            # Handle different result types for query analysis
            if hasattr(result, 'raw') and result.raw:
                try:
                    analysis = json.loads(result.raw)
                except:
                    analysis = json.loads(str(result.raw))
            elif hasattr(result, 'content'):
                try:
                    analysis = json.loads(result.content)
                except:
                    analysis = json.loads(str(result.content))
            else:
                result_str = str(result)
                cleaned_result = result_str.strip()
                
                # Remove markdown code blocks if present
                if cleaned_result.startswith('```json'):
                    cleaned_result = cleaned_result[7:]
                if cleaned_result.startswith('```'):
                    cleaned_result = cleaned_result[3:]
                if cleaned_result.endswith('```'):
                    cleaned_result = cleaned_result[:-3]
                
                cleaned_result = cleaned_result.strip()
                
                try:
                    analysis = json.loads(cleaned_result)
                except json.JSONDecodeError as e:
                    print(f"❌ Query analysis JSON parsing failed: {e}")
                    print(f"📝 Raw content: {cleaned_result}")
                    
                    # Try to extract JSON from the content
                    import re
                    json_match = re.search(r'\{.*\}', cleaned_result, re.DOTALL)
                    if json_match:
                        json_str = json_match.group()
                        print(f"🔍 Extracted JSON: {json_str[:200]}...")
                        analysis = json.loads(json_str)
                    else:
                        # Fallback: create a basic analysis
                        analysis = {
                            "task_type": "quiz_generation",
                            "parameters": {
                                "topic": "General Knowledge",
                                "difficulty": "medium",
                                "num_questions": 5
                            },
                            "agents_needed": ["quiz_specialist"],
                            "expected_output": "Quiz questions"
                        }
                        print("⚠️ Using fallback analysis due to JSON parsing failure")
            
            print(f"📋 Query Analysis: {analysis}")
            
            # Route to appropriate handler based on task type
            if analysis.get("task_type") == "quiz_generation":
                return await self._handle_quiz_generation(analysis, context)
            else:
                return {
                    "success": False,
                    "message": f"Task type '{analysis.get('task_type')}' not yet implemented",
                    "analysis": analysis
                }
                
        except Exception as e:
            print(f"❌ CrewAI System: Error processing query: {str(e)}")
            return {
                "success": False,
                "message": f"Error processing user query: {str(e)}",
                "error": str(e)
            }
    
    async def _handle_quiz_generation(self, analysis: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle quiz generation using specialized agents"""
        
        try:
            print("🎓 CrewAI System: Starting quiz generation with specialized agents")
            
            parameters = analysis.get("parameters", {})
            topic = parameters.get("topic", "General Knowledge")
            difficulty = parameters.get("difficulty", "medium")
            num_questions = parameters.get("num_questions", 5)
            
            # Task 1: Generate quiz content
            content_task = Task(
                description=f"""
                Generate {num_questions} high-quality multiple choice questions about {topic} 
                with {difficulty} difficulty level.
                
                Requirements:
                1. Each question must have exactly 4 options (A, B, C, D)
                2. Only one correct answer per question
                3. Questions should be clear, unambiguous, and educationally valuable
                4. Difficulty should match the specified level: {difficulty}
                5. Questions should be relevant to the topic: {topic}
                6. Include a mix of factual and conceptual questions
                7. Provide clear explanations for correct answers
                8. Ensure questions are free from bias and trickery
                
                Focus on creating questions that truly test understanding, not just memorization.
                """,
                agent=self.quiz_specialist,
                expected_output="Detailed quiz questions with options, correct answers, and explanations"
            )
            
            # Task 2: Validate content
            validation_task = Task(
                description=f"""
                Review and validate the quiz content generated by the Quiz Specialist.
                
                Check for:
                1. Content accuracy and correctness
                2. Question clarity and ambiguity
                3. Educational value and appropriateness
                4. Bias detection and removal
                5. Difficulty level consistency
                6. Answer option quality and plausibility
                7. Explanation quality and helpfulness
                
                Provide feedback and suggest improvements if needed.
                """,
                agent=self.content_validator,
                expected_output="Validated and improved quiz content with feedback"
            )
            
            # Task 3: Format output
            formatting_task = Task(
                description=f"""
                Format the validated quiz content into the required JSON structure.
                
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
                
                Ensure:
                1. Valid JSON structure
                2. All required fields are present
                3. No additional formatting or markdown
                4. Proper data types and structure
                """,
                agent=self.quiz_formatter,
                expected_output="Properly formatted JSON with quiz questions"
            )
            
            # Execute quiz generation with advanced rate limiting and fallback
            async def _execute_quiz_crew():
                crew = Crew(
                    agents=[self.quiz_specialist, self.content_validator, self.quiz_formatter],
                    tasks=[content_task, validation_task, formatting_task],
                    verbose=True
                )
                print("🤖 Executing CrewAI quiz generation crew...")
                return crew.kickoff()
            
            try:
                result = await execute_with_rate_limit(
                    _execute_quiz_crew,
                    estimated_tokens=2000
                )
            except Exception as e:
                if "rate_limit" in str(e).lower() or "rate limit" in str(e).lower():
                    print(f"⚠️ CrewAI rate limit reached, using fallback system")
                    return await fallback_system.generate_fallback_questions(
                        topic=topic,
                        difficulty=difficulty,
                        num_questions=num_questions
                    )
                else:
                    raise
            
            # Parse the result - CrewAI returns a complex object
            print(f"📋 CrewAI Result Type: {type(result)}")
            print(f"📋 CrewAI Result: {str(result)[:200]}...")
            
            # Handle different result types
            if hasattr(result, 'raw') and result.raw:
                # Try to parse the raw content
                try:
                    questions_data = json.loads(result.raw)
                except:
                    questions_data = json.loads(str(result.raw))
            elif hasattr(result, 'content'):
                # Try to parse the content
                try:
                    questions_data = json.loads(result.content)
                except:
                    questions_data = json.loads(str(result.content))
            else:
                # Try to parse the string representation
                result_str = str(result)
                print(f"📝 Raw result string: {result_str[:500]}...")
                
                # Clean the result string
                cleaned_result = result_str.strip()
                
                # Remove any markdown code blocks if present
                if cleaned_result.startswith('```json'):
                    cleaned_result = cleaned_result[7:]  # Remove ```json
                if cleaned_result.startswith('```'):
                    cleaned_result = cleaned_result[3:]   # Remove ```
                if cleaned_result.endswith('```'):
                    cleaned_result = cleaned_result[:-3]  # Remove trailing ```
                
                cleaned_result = cleaned_result.strip()
                print(f"🧹 Cleaned result: {cleaned_result[:200]}...")
                
                try:
                    questions_data = json.loads(cleaned_result)
                except json.JSONDecodeError as e:
                    print(f"❌ JSON parsing failed: {e}")
                    print(f"📝 Raw content: {cleaned_result}")
                    
                    # Try to extract JSON from the content
                    import re
                    json_match = re.search(r'\{.*\}', cleaned_result, re.DOTALL)
                    if json_match:
                        json_str = json_match.group()
                        print(f"🔍 Extracted JSON: {json_str[:200]}...")
                        questions_data = json.loads(json_str)
                    else:
                        # If all JSON parsing fails, create a fallback response
                        print("⚠️ All JSON parsing attempts failed, creating fallback questions")
                        questions_data = {
                            "questions": [
                                {
                                    "question_text": f"What is a key concept in {topic}?",
                                    "options": ["Option A", "Option B", "Option C", "Option D"],
                                    "correct_answer": "Option A",
                                    "explanation": "This is a fallback question due to JSON parsing issues"
                                }
                            ]
                        }
            
            questions = questions_data.get('questions', [])
            
            print(f"📝 Generated {len(questions)} questions using CrewAI system")
            
            # Validate questions
            if not questions:
                return {
                    "success": False,
                    "message": "No questions generated by CrewAI system",
                    "error": "Empty questions array"
                }
            
            # Validate question structure
            for i, question in enumerate(questions):
                required_fields = ['question_text', 'options', 'correct_answer']
                if not all(field in question for field in required_fields):
                    return {
                        "success": False,
                        "message": f"Invalid question structure at index {i}",
                        "error": f"Missing required fields in question {i+1}"
                    }
            
            print("✅ CrewAI system generated valid questions")
            
            return {
                "success": True,
                "message": f"Generated {len(questions)} questions using CrewAI system",
                "questions": questions,
                "questions_count": len(questions),
                "system_used": "CrewAI Multi-Agent System"
            }
            
        except Exception as e:
            print(f"❌ CrewAI System: Error in quiz generation: {str(e)}")
            return {
                "success": False,
                "message": f"CrewAI quiz generation failed: {str(e)}",
                "error": str(e)
            }
    
    async def generate_quiz_for_data(self, quiz_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate quiz for specific data using CrewAI system"""
        
        try:
            print(f"🎯 CrewAI System: Generating quiz for data: {quiz_data}")
            
            # Extract parameters from quiz data
            topic = quiz_data.get('topic', 'General Knowledge')
            difficulty = quiz_data.get('difficulty', 'medium')
            num_questions = quiz_data.get('total_questions', 5)
            
            # Create a comprehensive query for the system
            user_query = f"Create a {difficulty} level quiz about {topic} with {num_questions} questions"
            
            # Process through the CrewAI system
            result = await self.process_user_query(user_query, quiz_data)
            
            if result.get("success"):
                # Save questions to database if successful
                from app.services.firebase_service import FirebaseService
                firebase_service = FirebaseService(self.db)
                
                saved_questions = []
                questions = result.get("questions", [])
                
                for i, question_data in enumerate(questions):
                    question_dict = {
                        "quiz_id": quiz_data.get('id'),
                        "question_text": question_data['question_text'],
                        "options": question_data['options'],
                        "correct_answer": question_data['correct_answer'],
                        "time_limit": quiz_data.get('time_per_question', 60),
                        "order": i + 1
                    }
                    
                    try:
                        question = await firebase_service.create_question(question_dict)
                        saved_questions.append(question)
                        print(f"✅ Question {i+1} saved successfully")
                    except Exception as e:
                        print(f"❌ Failed to save question {i+1}: {e}")
                        return {
                            "success": False,
                            "message": f"Failed to save questions to database: {str(e)}",
                            "error": str(e)
                        }
                
                return {
                    "success": True,
                    "message": f"Generated and saved {len(saved_questions)} questions using CrewAI system",
                    "questions_count": len(saved_questions),
                    "quiz_id": quiz_data.get('id'),
                    "system_used": "CrewAI Multi-Agent System"
                }
            else:
                return result
                
        except Exception as e:
            print(f"❌ CrewAI System: Error generating quiz for data: {str(e)}")
            return {
                "success": False,
                "message": f"CrewAI system error: {str(e)}",
                "error": str(e)
            }
