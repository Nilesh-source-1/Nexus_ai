
import os
from dotenv import load_dotenv
from google import genai

# Load API key from .env
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

# Check API key
if not API_KEY:
    raise ValueError("Gemini API key not found!")

# Connect to Gemini
client = genai.Client(api_key=API_KEY)

MODEL = "gemini-3.5-flash-lite"


def ask_nexus(prompt):
    """Send a prompt to Gemini and return its response."""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    return response.text


if __name__ == "__main__":
    answer = ask_nexus("Introduce yourself as NEXUS AI in two sentences.")
    print("\nNEXUS AI RESPONSE:\n")
    print(answer)
