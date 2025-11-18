import os
import json
from google import genai
from google.genai.errors import APIError
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
AI_CLIENT = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


def generate_questions_for_level(level_name, question_type, num_questions=2):
    """Generates structured JSON questions using the Gemini API."""
    if not AI_CLIENT:
        print("Gemini API key not found. Returning mock data.")
        return []

    prompt = f"""
    Generate {num_questions} unique, short {question_type} questions for a Level {level_name} software engineering interview.
    Format the output STRICTLY as a JSON array of dictionaries with 'title' and 'type' keys.
    Use 'type': 'TEXT' for open answers, and 'type': 'CHOICE' for MCQs.
    If 'type' is 'CHOICE', include an 'options' array.
    """

    try:
        response = AI_CLIENT.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )

        # Robust parsing to remove markdown fences if present
        json_text = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(json_text)

    except APIError as e:
        print(f"Error calling Gemini API: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"JSON parsing error from AI response: {e}. Raw output: {response.text}")
        return []