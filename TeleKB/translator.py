import os
from google import genai
from .config import Config

class Translator:
    def __init__(self):
        if Config.GEMINI_API_KEY:
            self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
            # Use gemini-1.5-flash as it is the current standard/cost-effective model.
            # gemini-pro (v1.0) is often deprecated or requires specific endpoints.
            # User requested the "latest fast version".
            # verified available: gemini-2.5-flash
            self.model_name = "gemini-2.5-flash"
        else:
            self.client = None

    def translate_to_korean(self, text: str) -> str:
        if not text or not self.client:
            return ""
        
        # Simple retry logic for 429 errors
        import time
        max_retries = 3
        
        for attempt in range(max_retries + 1):
            try:
                prompt = f"Translate the following text to Korean. Output ONLY the translation without any explanation or quotes:\n\n{text}"
                
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                
                if response.text:
                    return response.text.strip()
                return ""
            except Exception as e:
                # Check for 429 or Resource Exhausted
                err_str = str(e)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    if attempt < max_retries:
                        sleep_time = 2 * (attempt + 1) # 2s, 4s, 6s...
                        print(f"Rate limit hit. Retrying in {sleep_time}s...")
                        time.sleep(sleep_time)
                        continue
                
                print(f"Translation error: {e}")
                return "" 
