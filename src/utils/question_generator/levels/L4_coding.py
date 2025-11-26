from src.utils.question_generator.core.llm_client import call_llm
from src.utils.question_generator.core.validator import extract_json


def generate_L4_questions(difficulty, count):
    prompt = f"""
Generate {count} coding challenges.

Each question must contain:
- title
- description
- input_format
- output_format
- constraints
- sample_input
- sample_output

Return JSON: {{ "questions": [ ... ] }}
"""

    text = call_llm(prompt)
    data = extract_json(text)
    return data
