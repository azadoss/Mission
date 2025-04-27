from google import genai
from config import GEMINI_API_KEY

def create_client():
    """Create and return a configured Gemini client."""
    client = genai.Client(
        api_key=GEMINI_API_KEY,
        http_options={
            'api_version': 'v1alpha',
        }
    )
    return client