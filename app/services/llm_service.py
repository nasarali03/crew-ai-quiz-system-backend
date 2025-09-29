import os
# Google Gemini disabled - using only Groq
genai = None
from groq import Groq
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        
        # Initialize only Groq (Google Gemini disabled)
        if self.groq_api_key:
            self.groq_client = Groq(api_key=self.groq_api_key)
            print("✅ Groq API initialized successfully")
        else:
            self.groq_client = None
            print("❌ Groq API key not configured")
    
    async def generate_with_gemini(self, prompt: str, **kwargs) -> str:
        """Google Gemini disabled - use Groq instead"""
        raise ValueError("Google Gemini is disabled. Please use Groq API.")
    
    async def generate_with_groq(self, prompt: str, model: str = "llama-3.1-8b-instant", **kwargs) -> str:
        """Generate text using Groq"""
        try:
            if not self.groq_api_key:
                raise ValueError("Groq API key not configured")
            
            if self.groq_client is None:
                raise ValueError("Groq client not initialized")
            
            print(f"🚀 Calling Groq API with model: {model}")
            print(f"📝 Prompt length: {len(prompt)} characters")
            
            response = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=model,
                temperature=0.7,
                max_tokens=4096,  # Increased for longer responses
                **kwargs
            )
            
            if not response.choices or not response.choices[0].message.content:
                raise Exception("Empty response from Groq API")
            
            content = response.choices[0].message.content.strip()
            print(f"✅ Groq API response length: {len(content)} characters")
            print(f"📝 Response preview: {content[:100]}...")
            return content
            
        except Exception as e:
            print(f"❌ Groq API error: {e}")
            raise e
    
    async def generate_quiz_questions(self, topic: str, difficulty: str, num_questions: int) -> Dict[str, Any]:
        """Generate quiz questions using the best available LLM"""
        prompt = f"""
        Generate {num_questions} multiple choice questions about {topic} with {difficulty} difficulty.
        
        Requirements:
        1. Each question should have exactly 4 options (A, B, C, D)
        2. Only one correct answer per question
        3. Questions should be clear and unambiguous
        4. Difficulty should match the specified level ({difficulty})
        5. Questions should be relevant to the topic: {topic}
        6. Include a mix of factual and conceptual questions
        
        IMPORTANT: Return ONLY valid JSON with no additional text, markdown, or explanations.
        Do not wrap the response in code blocks or add any formatting.
        
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
        """
        
        # Use only Groq (Google Gemini disabled)
        try:
            if self.groq_api_key:
                print(f"🤖 Using Groq API to generate {num_questions} questions about {topic}")
                response = await self.generate_with_groq(prompt)
            else:
                raise ValueError("Groq API key not configured. Google Gemini is disabled.")
            
            print(f"✅ LLM Response received: {response[:200]}...")
            
            # Clean and parse JSON response
            import json
            import re
            
            # Remove any markdown code blocks if present
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]  # Remove ```json
            if cleaned_response.startswith('```'):
                cleaned_response = cleaned_response[3:]   # Remove ```
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]  # Remove trailing ```
            
            cleaned_response = cleaned_response.strip()
            print(f"🧹 Cleaned response: {cleaned_response[:200]}...")
            
            # Try to parse JSON
            try:
                parsed_response = json.loads(cleaned_response)
                print(f"✅ Parsed {len(parsed_response.get('questions', []))} questions from LLM")
                return parsed_response
            except json.JSONDecodeError as json_error:
                print(f"❌ JSON parsing failed: {json_error}")
                print(f"📝 Raw response: {cleaned_response}")
                raise Exception(f"Invalid JSON response from LLM: {str(json_error)}")
            
        except Exception as e:
            print(f"❌ Error generating quiz questions with LLM: {e}")
            print(f"🚫 LLM FAILED - NO FALLBACK DATA WILL BE INSERTED")
            # Do NOT return fallback questions - let the error propagate
            raise Exception(f"LLM failed to generate questions: {str(e)}")
    
    async def generate_email_content(self, student_name: str, quiz_title: str, quiz_link: str) -> Dict[str, str]:
        """Generate personalized email content"""
        prompt = f"""
        Create a personalized email invitation for a student to take a quiz.
        
        Student Name: {student_name}
        Quiz Title: {quiz_title}
        Quiz Link: {quiz_link}
        
        Requirements:
        1. Write a warm, personalized greeting using the student's name
        2. Explain what the quiz is about and why it's important
        3. Provide clear instructions on how to take the quiz
        4. Include the quiz link prominently
        5. End with an encouraging message
        6. Keep the tone professional but friendly
        
        Return the email in this format:
        {{
            "subject": "Quiz Invitation - [Quiz Title]",
            "body": "Email body here"
        }}
        """
        
        try:
            if self.groq_api_key:
                response = await self.generate_with_groq(prompt)
            else:
                raise ValueError("Groq API key not configured. Google Gemini is disabled.")
            
            import json
            return json.loads(response)
            
        except Exception as e:
            print(f"Error generating email content: {e}")
            return self._get_fallback_email(student_name, quiz_title, quiz_link)
    
    async def analyze_video_transcript(self, transcript: str, required_topic: str) -> Dict[str, Any]:
        """Analyze video transcript for topic coverage"""
        prompt = f"""
        Analyze the following video transcript for topic coverage and content quality.
        
        Required Topic: {required_topic}
        Video Transcript: {transcript[:2000]}...
        
        Requirements:
        1. Evaluate how well the video covers the required topic (0.0 to 1.0 score)
        2. Identify key concepts mentioned
        3. Assess content quality and depth
        4. Note any off-topic content
        5. Provide specific feedback on topic coverage
        
        Return analysis in this format:
        {{
            "topic_coverage": 0.85,
            "key_concepts": ["concept1", "concept2", "concept3"],
            "content_quality": "high|medium|low",
            "feedback": "Detailed feedback about the video content",
            "off_topic_content": ["item1", "item2"],
            "overall_assessment": "Overall assessment of the video"
        }}
        """
        
        try:
            if self.groq_api_key:
                response = await self.generate_with_groq(prompt)
            else:
                raise ValueError("Groq API key not configured. Google Gemini is disabled.")
            
            import json
            return json.loads(response)
            
        except Exception as e:
            print(f"Error analyzing transcript: {e}")
            return self._get_fallback_analysis(required_topic)
    
    # Removed fallback methods - no mock data should be inserted
    
    # All fallback methods removed - no mock data should be inserted
