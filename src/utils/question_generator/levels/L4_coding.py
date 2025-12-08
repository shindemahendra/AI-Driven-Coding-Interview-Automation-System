from src.utils.question_generator.core.llm_client import call_llm
from src.utils.question_generator.core.validator import extract_json


def generate_L4_questions(difficulty, count):
    prompt = f"""
Generate EXACTLY {count} coding questions with:
title, description, input_format, output_format, constraints, sample_input, sample_output
difficulty="{difficulty}"
Strict JSON:
{{ "questions": [ ... ] }}
"""

    raw = call_llm(prompt)
    parsed = extract_json(raw)

    if isinstance(parsed, dict):
        parsed = parsed.get("questions", [])

    return parsed
