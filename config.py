# config.py
import os
from dotenv import load_dotenv

load_dotenv() 

class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    # Model selection — changeable per environment
    LLM_MODEL = os.getenv("LLM_MODEL","llama-3.3-70b-versatile")

# Global instance
config = Config()