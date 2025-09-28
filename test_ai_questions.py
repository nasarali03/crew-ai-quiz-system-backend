#!/usr/bin/env python3
"""
Test script to generate AI questions and print them to terminal
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.llm_service import LLMService

async def test_ai_questions():
    """Test AI question generation and print to terminal"""
    try:
        print("🤖 Testing AI Question Generation...")
        print("=" * 60)
        
        # Initialize LLM service
        llm_service = LLMService()
        
        # Check if Groq API key is configured
        if not llm_service.groq_api_key:
            print("❌ Groq API key not configured!")
            print("Please set GROQ_API_KEY in your .env file")
            return
        
        print(f"🔑 Groq API Key configured: {bool(llm_service.groq_api_key)}")
        print("=" * 60)
        
        # Generate questions using AI
        print("🚀 Generating AI questions...")
        questions_data = await llm_service.generate_quiz_questions(
            topic="Python Programming",
            difficulty="medium",
            num_questions=5
        )
        
        questions = questions_data.get('questions', [])
        print(f"📝 Generated {len(questions)} AI questions:")
        print("=" * 60)
        
        for i, question in enumerate(questions, 1):
            print(f"\n🔢 Question {i}:")
            print(f"❓ {question.get('question_text', 'No question text')}")
            print("📋 Options:")
            
            options = question.get('options', [])
            correct_answer = question.get('correct_answer', '')
            
            for j, option in enumerate(options, 1):
                marker = "✅" if option == correct_answer else "  "
                print(f"   {marker} {chr(64+j)}. {option}")
            
            print(f"💡 Explanation: {question.get('explanation', 'No explanation')}")
            print("-" * 40)
        
        print(f"\n✅ Successfully generated {len(questions)} AI questions!")
        print("=" * 60)
        
        return questions
        
    except Exception as e:
        print(f"❌ AI question generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("🧪 AI Question Generation Test")
    print("=" * 60)
    
    # Run the async function
    questions = asyncio.run(test_ai_questions())
    
    if questions:
        print(f"\n🎉 Test completed successfully! Generated {len(questions)} questions.")
    else:
        print("\n❌ Test failed!")
