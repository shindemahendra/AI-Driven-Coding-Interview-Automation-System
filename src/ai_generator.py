import os
import json
from google import genai
from google.genai.errors import APIError
from dotenv import load_dotenv

# Load GEMINI_API_KEY from .env file
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
AI_CLIENT = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


def generate_questions_for_level(level_name, question_type, num_questions=3):
    """Generates structured JSON questions using the Gemini API."""
    if not AI_CLIENT:
        print("Warning: Gemini API key not found. Returning mock data.")
        return [
            {"title": f"Candidate Full Name", "type": "TEXT"},
            {"title": f"What is the time complexity of Bubble Sort? ({level_name})", "type": "TEXT"}
        ]

    prompt = f"""
    Generate {num_questions} unique, short, relevant questions for a Level {level_name} interview focusing on {question_type}.

    For coding/essay questions (L4/L5), use 'type': 'TEXT'.
    For L2 (MCQs), use 'type': 'CHOICE' and include an 'options' array with 4 choices.

    Format the output STRICTLY as a JSON array of dictionaries.

    Example for TEXT:
    [
        {{"title": "Explain the difference between a process and a thread.", "type": "TEXT"}}
    ]

    Example for CHOICE (MCQ):
    [
        {{"title": "Which data structure is typically used to implement a recursive function call stack?", 
          "type": "CHOICE", 
          "options": ["Queue", "Heap", "Stack", "Array"]}}
    ]
    """

    try:
        response = AI_CLIENT.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )

        json_text = response.text.strip()
        if json_text.startswith('```json'):
            json_text = json_text.strip('```json').strip('```')

        return json.loads(json_text)

    except APIError as e:
        print(f"Error calling Gemini API: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"JSON parsing error from AI response: {e}. Raw output: {response.text}")
        return []