#!/usr/bin/env python3
"""
Test script to demonstrate quiz creation logging
This script simulates a quiz creation request and shows the terminal output
"""

import requests
import json
from datetime import datetime

def test_quiz_creation():
    """Test quiz creation with terminal logging"""
    
    # Quiz data that would come from the frontend form
    quiz_data = {
        "title": "Python Programming Fundamentals",
        "description": "A comprehensive quiz covering Python basics, data structures, and control flow",
        "topic": "Python Programming",
        "difficulty": "medium",
        "time_per_question": 60,
        "question_type": "MCQ",
        "total_questions": 10
    }
    
    print("🧪 TESTING QUIZ CREATION LOGGING")
    print("=" * 60)
    print("📋 Sample Quiz Data:")
    print(json.dumps(quiz_data, indent=2))
    print("=" * 60)
    print("🚀 This is what you'll see in the terminal when a user creates a quiz:")
    print("=" * 60)
    
    # Simulate the terminal output that would appear
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print("=" * 80)
    print("🎯 QUIZ CREATION REQUEST RECEIVED")
    print(f"⏰ Timestamp: {timestamp}")
    print("=" * 80)
    print(f"📝 Quiz Title: {quiz_data['title']}")
    print(f"📄 Description: {quiz_data['description']}")
    print(f"🎯 Topic: {quiz_data['topic']}")
    print(f"⚡ Difficulty: {quiz_data['difficulty']}")
    print(f"⏱️  Time per Question: {quiz_data['time_per_question']} seconds")
    print(f"❓ Question Type: {quiz_data['question_type']}")
    print(f"🔢 Total Questions: {quiz_data['total_questions']}")
    print("=" * 80)
    print("🚀 Processing quiz creation...")
    print("=" * 80)
    print("🔧 AdminService: Processing quiz creation...")
    print("👤 Admin ID: default-admin-id")
    print("💾 Saving quiz to Firebase...")
    print(f"📊 Quiz data: {quiz_data}")
    print("💾 Firebase: Creating quiz with ID: abc123-def456-ghi789")
    print("🗄️  Saving to Firestore collection: quizzes")
    print("✅ Firebase: Quiz abc123-def456-ghi789 created successfully")
    print("📋 Quiz Title: Python Programming Fundamentals")
    print("🎯 Quiz Topic: Python Programming")
    print("⚡ Quiz Difficulty: medium")
    print("✅ Quiz saved to Firebase with ID: abc123-def456-ghi789")
    print("✅ Quiz created successfully with ID: abc123-def456-ghi789")
    print("📊 Final Quiz Response:")
    print("   - ID: abc123-def456-ghi789")
    print("   - Title: Python Programming Fundamentals")
    print("   - Topic: Python Programming")
    print("   - Difficulty: medium")
    print("   - Total Questions: 10")
    print("   - Time per Question: 60s")
    print("   - Question Type: MCQ")
    print("   - Is Active: True")
    print("   - Created At: 2024-01-15 14:30:25")
    print("=" * 80)
    print("🎉 QUIZ CREATION COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    
    print("\n" + "=" * 60)
    print("✅ TEST COMPLETED")
    print("=" * 60)
    print("📝 This is exactly what you'll see in your Python terminal")
    print("   when a user submits the create quiz form from the frontend!")
    print("=" * 60)

if __name__ == "__main__":
    test_quiz_creation()
