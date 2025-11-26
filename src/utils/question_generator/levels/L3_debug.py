from google.generativeai import GenerativeModel
from src.utils.question_generator.core.validator import extract_json

model = GenerativeModel("gemini-2.0-flash")


def generate_L3_questions(difficulty, total_count):
    final_questions = []
    batch_size = 20
    batches = total_count // batch_size

    for b in range(batches):
        print(f"   → L3 Batch {b+1}/{batches}")

        prompt = f"""
Generate EXACTLY {batch_size} debugging MCQ questions for Python.

VERY IMPORTANT:
- DO NOT USE CODE BLOCKS (no ```python)
- If code is needed, return it as a single-line string with \\n where needed.
- JSON MUST BE VALID.
- Escape all quotes inside strings.

Return ONLY a JSON array like:

[
  {{
    "question": "Bug description...",
    "code": "single line python code with \\n escape",
    "options": ["A", "B", "C", "D"],
    "correct_answer": "A",
    "topic": "L3",
    "difficulty": "{difficulty}"
  }}
]
"""

        for attempt in range(10):
            try:
                resp = model.generate_content(prompt)
                raw = resp.text.strip()

                data = extract_json(raw)

                # Some attempts may produce fewer/more: strict check
                if len(data) == batch_size:
                    final_questions.extend(data)
                    print("      ✔ Clean L3 batch added")
                    break
                else:
                    print(f"      ⚠ Wrong count {len(data)}, retrying…")

            except Exception as e:
                print(f"      ⚠ JSON error: {e}, retrying…")

    print(f"✔ Total L3 built: {len(final_questions)}")
    return final_questions
