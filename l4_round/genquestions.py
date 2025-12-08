import os
import json
from json_repair import repair_json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel(
    "models/gemini-2.0-flash",
    generation_config={
        "response_mime_type": "application/json"
    }
)

PROMPT = """
Generate EXACTLY 20 Python questions with:
- title
- clear detailed description
- difficulty (BASIC, MEDIUM, HARD)
- 3 public tests (input, expected)
- 15 hidden tests (input, expected)
Output ONLY a JSON array.
"""

print("Generating 20 questions...\n")

response = model.generate_content(PROMPT)

raw_json = response.candidates[0].content.parts[0].text

# ⭐ FIX ANY BROKEN JSON AUTOMATICALLY ⭐
fixed_json = repair_json(raw_json)

try:
    questions = json.loads(fixed_json)
except Exception as e:
    print("❌ Still invalid after repair.\nRAW:\n", raw_json)
    print("\nFIXED:\n", fixed_json)
    print("\nError:", e)
    raise SystemExit

with open("questions.json", "w", encoding="utf-8") as f:
    json.dump(questions, f, indent=4, ensure_ascii=False)

print("✔ Saved questions.json successfully!")
