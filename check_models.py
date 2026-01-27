import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    # Use dummy if not found, just to test import, but actually we need valid key to list models.
    # In this environment .env is in root.
    pass

client = genai.Client(api_key=api_key)

try:
    print("Listing models...")
    # New SDK might have client.models.list() or similar.
    # Let's check the doc or try common patterns.
    # Reference: Client.models.list()
    
    # iterate over models
    for m in client.models.list():
        print(f"Model: {m.name}")
        # print(m)
except Exception as e:
    print(f"Error: {e}")
