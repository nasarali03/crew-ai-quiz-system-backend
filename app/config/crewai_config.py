"""
CrewAI Configuration for Groq LLM
"""

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

def configure_crewai_groq():
    """Configure CrewAI to use Groq LLM with proper error handling"""
    
    try:
        # Set Groq API key
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        # Test Groq connection
        groq_client = Groq(api_key=groq_api_key)
        
        # Set environment variables for CrewAI
        os.environ["GROQ_API_KEY"] = groq_api_key
        
        # Configure CrewAI to use Groq
        os.environ["CREWAI_LLM_PROVIDER"] = "groq"
        os.environ["CREWAI_GROQ_MODEL"] = "llama-3.1-8b-instant"
        os.environ["CREWAI_GROQ_TEMPERATURE"] = "0.7"
        
        print("✅ CrewAI configured to use Groq LLM")
        print(f"🤖 Model: llama-3.1-8b-instant")
        print(f"🌡️ Temperature: 0.7")
        print(f"🔑 API Key configured: {bool(groq_api_key)}")
        
        return True
        
    except Exception as e:
        print(f"❌ CrewAI configuration failed: {str(e)}")
        return False

def get_groq_llm():
    """Get configured Groq LLM for CrewAI"""
    try:
        from langchain_groq import ChatGroq
        
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY not found")
        
        return ChatGroq(
            groq_api_key=groq_api_key,
            model_name="llama-3.1-8b-instant",
            temperature=0.7
        )
    except Exception as e:
        print(f"❌ Failed to create Groq LLM: {str(e)}")
        return None

def get_crewai_llm():
    """Get LLM configured for CrewAI using LiteLLM format"""
    try:
        from crewai import LLM
        
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY not found")
        
        # Configure CrewAI LLM with Groq
        llm = LLM(
            model="groq/llama-3.1-8b-instant",
            api_key=groq_api_key,
            temperature=0.7
        )
        
        return llm
    except Exception as e:
        print(f"❌ Failed to create CrewAI LLM: {str(e)}")
        return None

# Initialize configuration
configure_crewai_groq()
