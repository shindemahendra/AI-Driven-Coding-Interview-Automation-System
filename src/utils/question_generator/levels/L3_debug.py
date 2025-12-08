from google.generativeai import GenerativeModel
from src.utils.question_generator.core.validator import extract_json

model = GenerativeModel("gemini-2.0-flash")


def generate_L3_questions(difficulty, total_count):
    final_questions = []
    batch_size = 20
    batches = total_count // batch_size

    for b in range(batches):
        print(f"→ L3 Batch {b+1}/{batches}")

        prompt = f"""
Generate EXACTLY {batch_size} debugging MCQs.
Code (if present) must use "\\n" for line breaks.
Fields: question, code(optional), options, correct_answer
topic="Debugging", difficulty="{difficulty}"
Strict JSON array only.
"""

        for _ in range(10):
            try:
                raw = model.generate_content(prompt).text.strip()
                parsed = extract_json(raw)

                if isinstance(parsed, dict):
                    parsed = parsed.get("questions", [])

                if len(parsed) == batch_size:
                    final_questions.extend(parsed)
                    print("✔ Batch OK")
                    break

                print("⚠ Wrong count → retry")

            except Exception as e:
                print(f"⚠ JSON error: {e}")

    print(f"✔ L3 Generated: {len(final_questions)}")
    return final_questions
