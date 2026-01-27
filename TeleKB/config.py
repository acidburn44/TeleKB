import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_ID = os.getenv("API_ID")
    API_HASH = os.getenv("API_HASH")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    DB_PATH = "telekb.db"
    
    @staticmethod
    def validate():
        if not Config.API_ID or not Config.API_HASH:
             raise ValueError("API_ID and API_HASH must be set in .env file or environment variables")
        if not Config.GEMINI_API_KEY:
             raise ValueError("GEMINI_API_KEY must be set in .env file or environment variables")

