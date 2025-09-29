"""
Optimized prompts to reduce token usage while maintaining quality
"""

def get_optimized_query_analysis_prompt(user_query: str, context: Dict = None) -> str:
    """Optimized prompt for query analysis"""
    return f"""Analyze: "{user_query}"
Context: {context or "None"}

Extract:
- task_type: quiz_generation|other
- topic: extracted topic
- difficulty: easy|medium|hard  
- num_questions: number
- agents_needed: ["agent1", "agent2"]

Return JSON only."""

def get_optimized_quiz_generation_prompt(topic: str, difficulty: str, num_questions: int) -> str:
    """Optimized prompt for quiz generation"""
    return f"""Generate {num_questions} {difficulty} questions about {topic}.

Requirements:
- 4 options per question
- 1 correct answer
- Clear explanations
- JSON format only

Return: {{"questions": [{{"question_text": "...", "options": [...], "correct_answer": "...", "explanation": "..."}}]}}"""

def get_optimized_validation_prompt() -> str:
    """Optimized prompt for content validation"""
    return """Review quiz content for:
- Accuracy
- Clarity  
- Educational value
- Bias removal

Provide feedback and return improved content in same JSON format."""

def get_optimized_formatting_prompt() -> str:
    """Optimized prompt for JSON formatting"""
    return """Format content as valid JSON:
{{"questions": [{{"question_text": "...", "options": [...], "correct_answer": "...", "explanation": "..."}}]}}

Ensure valid JSON structure only."""

# Token estimation functions
def estimate_tokens(text: str) -> int:
    """Rough token estimation (1 token ≈ 4 characters)"""
    return len(text) // 4

def get_prompt_token_estimates() -> Dict[str, int]:
    """Get token estimates for different prompt types"""
    return {
        "query_analysis": 200,
        "quiz_generation": 800,
        "content_validation": 600,
        "json_formatting": 300
    }
