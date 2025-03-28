from google import genai
from dotenv import load_dotenv
from .translate_utils import TranslateResponse, translate_prompt
import os

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY", "")

client = genai.Client(api_key=API_KEY)

def translate(text, language="English", model=None):
    if model is None:
        model = "gemini-2.0-flash"
    try:
        response = client.models.generate_content(
            model=model,
            contents= translate_prompt(text, language),
            config={
                'response_mime_type': 'application/json',
                'response_schema': TranslateResponse,
            }
        )
    except Exception as e:
        print(f"Error during translation: {e}")
        raise
    return response.parsed