from src.utils.question_generator.core.llm_client import call_llm
from src.utils.question_generator.core.validator import extract_json


def generate_L1_questions(difficulty, count):
    prompt = f"""
Generate EXACTLY {count} logical reasoning MCQs.
Rules:
- Logical reasoning only
- 4 MCQ options (A,B,C,D)
- STRICT JSON
Difficulty = "{difficulty}"

JSON format:
[
  {{
    "question": "",
    "options": ["A","B","C","D"],
    "correct_answer": "A",
    "difficulty": "{difficulty}",
    "topic": "Logic"
  }}
]
"""

    raw = call_llm(prompt)
    parsed = extract_json(raw)

    if isinstance(parsed, dict):
        parsed = parsed.get("questions", [])

    return parsed
