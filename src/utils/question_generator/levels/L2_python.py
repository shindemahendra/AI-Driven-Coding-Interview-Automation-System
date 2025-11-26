import json
from google.generativeai import GenerativeModel
from src.utils.question_generator.core.validator import extract_json

model = GenerativeModel("gemini-2.0-flash")

def generate_L2_questions(difficulty, total_count):
    final_questions = []
    batch_size = 20
    batches = total_count // batch_size

    for b in range(batches):
        print(f"   → L2 Batch {b+1}/{batches}")

        prompt = f"""
Generate EXACTLY {batch_size} Python MCQ interview questions.
Difficulty: {difficulty}

Return ONLY pure JSON array like:

[
  {{
    "question": "...",
    "options": ["A", "B", "C", "D"],
    "correct_answer": "A",
    "topic": "Python",
    "difficulty": "{difficulty}"
  }}
]
"""

        for attempt in range(10):
            try:
                resp = model.generate_content(prompt)
                raw = resp.text.strip()

                data = extract_json(raw)

                # sometimes gemini returns more or fewer — ensure EXACT count
                if len(data) == batch_size:
                    final_questions.extend(data)
                    print("      ✔ Clean batch added")
                    break
                else:
                    print(f"      ⚠ Wrong count {len(data)}, retrying…")

            except Exception as e:
                print(f"      ⚠ JSON error: {e}, retrying…")

    print(f"✔ Total L2 built: {len(final_questions)}")
    return final_questions
