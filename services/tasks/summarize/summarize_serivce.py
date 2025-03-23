from google import genai
from dotenv import load_dotenv
from .summarize_utils import SummarizeResponse, summarize_prompt
from ..common_enums import TextStyle, EducationLevel, LearningOutcome
import os

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY", "")

client = genai.Client(api_key=API_KEY)

def summary(text, model=None, style=TextStyle.STANDARD, education_level=EducationLevel.HIGH_SCHOOL, learning_outcome=LearningOutcome.DECLARATIVE):
    if model is None:
        model = "gemini-2.0-flash"
    response = client.models.generate_content(
        model=model,
        contents= summarize_prompt(text, style, education_level, learning_outcome),
        config={
            'response_mime_type': 'application/json',
            'response_schema': SummarizeResponse,
        }
    )
    return response.parsed