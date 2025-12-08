from google.generativeai import GenerativeModel
from src.utils.question_generator.core.validator import extract_json

model = GenerativeModel("gemini-2.0-flash")


def generate_L5_questions(difficulty: str, total_count: int):
    final = []
    batch_size = 20
    batches = total_count // batch_size

    for b in range(batches):
        print(f"→ L5 Batch {b+1}/{batches}")

        prompt = f"""
Generate EXACTLY {batch_size} soft-skill MCQs.
Simple one-sentence options.
No explanations.
Strict JSON list only.
difficulty="{difficulty}"
topic="Soft Skills"
"""

        for _ in range(10):
            try:
                raw = model.generate_content(prompt).text.strip()
                parsed = extract_json(raw)

                if isinstance(parsed, dict):
                    parsed = parsed.get("questions", [])

                if len(parsed) == batch_size:
                    final.extend(parsed)
                    print("✔ Batch OK")
                    break

                print("⚠ Wrong count → retry")

            except Exception as e:
                print(f"⚠ JSON error: {e}")

    print(f"✔ L5 Generated: {len(final)}")
    return final
