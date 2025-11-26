import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-2.0-flash"


def call_llm(prompt, retries=3):
    for _ in range(retries):
        try:
            response = genai.GenerativeModel(MODEL).generate_content(prompt)
            return response.text
        except Exception as e:
            print("⚠ LLM error, retrying...", e)
    raise Exception("LLM failed after retries")
