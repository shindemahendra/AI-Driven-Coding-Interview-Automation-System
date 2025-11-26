from src.utils.question_generator.core.llm_client import call_llm
from src.utils.question_generator.core.validator import extract_json


def generate_L1_questions(difficulty, count):
    prompt = f"""
Generate {count} logical reasoning MCQs for IT hiring assessments.

Difficulty: {difficulty}
Rules:
- Only logical puzzles, patterns, sequences, analytical reasoning.
- No Python, no coding, no softskills.
- 4 valid MCQ options.
- Output STRICT JSON with fields:
  question, options, correct_answer

Return JSON:
{{
  "questions": [
      {{
          "question": "...",
          "options": ["A", "B", "C", "D"],
          "correct_answer": "B"
      }}
  ]
}}
"""

    text = call_llm(prompt)
    data = extract_json(text)
    return data
