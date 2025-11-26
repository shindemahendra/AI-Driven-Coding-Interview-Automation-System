from google.generativeai import GenerativeModel
from src.utils.question_generator.core.validator import extract_json

model = GenerativeModel("gemini-2.0-flash")


def generate_L5_questions(difficulty: str, total_count: int):
    final_questions = []
    batch_size = 20
    batches = total_count // batch_size

    for b in range(batches):
        print(f"   → L5 Batch {b+1}/{batches}")

        prompt = f"""
Generate EXACTLY {batch_size} soft-skill / behavioural MCQs.

IMPORTANT RULES (strict):
- DO NOT use commas inside the "correct_answer".
- DO NOT use double quotes inside any option. Replace quotes with single quote.
- NO multi-sentence options. Keep each option short, clear, single-sentence.
- JSON MUST be valid and safe.
- No bullet points.
- No explanations.
- ONLY plain text values.

Return ONLY a JSON array with items like:

[
  {{
    "question": "Short behavioural question?",
    "options": ["Option1", "Option2", "Option3", "Option4"],
    "correct_answer": "Option2",
    "topic": "L5",
    "difficulty": "{difficulty}"
  }}
]
"""

        for attempt in range(10):
            try:
                resp = model.generate_content(prompt)
                raw = resp.text.strip()

                data = extract_json(raw)

                # strict item count
                if len(data) == batch_size:
                    final_questions.extend(data)
                    print("      ✔ Clean L5 batch added")
                    break
                else:
                    print(f"      ⚠ Wrong count {len(data)} — retrying…")

            except Exception as e:
                print(f"      ⚠ JSON error: {e} — retrying…")

    print(f"✔ Total L5 built: {len(final_questions)}")
    return final_questions
