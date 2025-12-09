import os
import yaml
import json
import random
from dotenv import load_dotenv
from google import genai

# Load API Key from .env
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("❌ GEMINI_API_KEY missing in .env")

client = genai.Client(api_key=API_KEY)

# Model and generation settings
MODEL_NAME = "gemini-1.5-flash"
TEST_PUBLIC = 3
TEST_HIDDEN = 12

# Question groups by difficulty
BATCH_PLAN = [
    {"basic": 2, "medium": 2, "hard": 1},  # batch1
    {"basic": 2, "medium": 2, "hard": 1},  # batch2
    {"basic": 2, "medium": 2, "hard": 1},  # batch3
    {"basic": 2, "medium": 2, "hard": 1},  # batch4
]


def build_prompt(basic, medium, hard):
    return f"""
Generate exactly {basic + medium + hard} Python coding questions.

For each question include ONLY these fields in YAML format:
- title: short name (no numbering)
- difficulty: BASIC or MEDIUM or HARD
- description: full problem statement
- public_tests: list of tests, each as:
    - input: VALUE
      expected: VALUE
- hidden_tests: same structure (but NOT revealing patterns)

Required counts:
• BASIC: {basic}
• MEDIUM: {medium}
• HARD: {hard}
• {TEST_PUBLIC} public_tests exactly
• {TEST_HIDDEN} hidden_tests exactly

Rules:
✔ ONLY YAML output — no markdown, no code fencing
✔ Difficulty must match requested count
✔ Tests must match function input clearly
✔ Each test must be a valid Python literal
✔ hidden_tests should not be trivial or duplicates
✔ Title must not repeat across questions
"""


def validate_questions(questions):
    """Ensure structure is correct."""
    if not isinstance(questions, list):
        raise ValueError("Questions must be a list")

    for q in questions:
        if "title" not in q:
            raise ValueError("Missing title")
        if "description" not in q:
            raise ValueError(f"Missing description for {q['title']}")
        if "difficulty" not in q:
            raise ValueError(f"Missing difficulty in {q['title']}")
        if "public_tests" not in q or len(q["public_tests"]) != TEST_PUBLIC:
            raise ValueError(f"{q['title']} must have exactly {TEST_PUBLIC} public tests")
        if "hidden_tests" not in q or len(q["hidden_tests"]) != TEST_HIDDEN:
            raise ValueError(f"{q['title']} must have exactly {TEST_HIDDEN} hidden tests")

    return True


def generate_batch(batch_cfg, index):
    print(f"\n📌 Generating Batch {index+1}: {batch_cfg}")

    prompt = build_prompt(
        batch_cfg["basic"],
        batch_cfg["medium"],
        batch_cfg["hard"]
    )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    text = response.text
    if not text:
        raise ValueError("Model returned empty response!")

    try:
        batch_data = yaml.safe_load(text)
    except Exception as e:
        print("\n❌ YAML ERROR OUTPUT:\n", text)
        raise ValueError("Generated YAML invalid") from e

    validate_questions(batch_data)
    print(f"✔ Batch {index+1} validated! ({len(batch_data)} questions)")
    return batch_data


def main():
    all_questions = []

    for idx, cfg in enumerate(BATCH_PLAN):
        batch = generate_batch(cfg, idx)
        all_questions.extend(batch)

    print(f"\n🎯 SUCCESS! Total Questions: {len(all_questions)}")

    with open("questions.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(all_questions, f, allow_unicode=True, sort_keys=False)

    print("\n📦 Saved: questions.yaml")


if __name__ == "__main__":
    main()
