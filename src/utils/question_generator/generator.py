# src/utils/question_generator/generator.py
import os
import json
import re
import time
from dotenv import load_dotenv
import google.generativeai as genai

from .prompt_templates import MCQ_PROMPT, CODING_PROMPT
from .save_manager import save

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-2.0-flash"

# --- helpers for robust JSON parsing ---
def write_raw_debug(level, difficulty, raw_text):
    os.makedirs("debug_output", exist_ok=True)
    fname = f"debug_output/{level}_{difficulty}_{int(time.time())}.txt"
    with open(fname, "w", encoding="utf-8") as f:
        f.write(raw_text)
    return fname

def try_json_loads(text):
    try:
        return json.loads(text)
    except:
        return None

def extract_json(text):
    """
    Try multiple strategies to extract/repair JSON from LLM response.
    Returns Python object or raises ValueError.
    """
    # 1) direct load
    obj = try_json_loads(text)
    if obj is not None:
        return obj

    # 2) try to find first [...] or {....}
    # prefer array for MCQs, object for coding
    # find longest bracketed substring that parses
    candidates = []

    # all bracketed substrings
    for match in re.finditer(r"(\[.*\]|\{.*\})", text, flags=re.DOTALL):
        s = match.group(0)
        candidates.append(s)

    # try candidates (longest first)
    candidates = sorted(set(candidates), key=lambda x: -len(x))
    for c in candidates:
        obj = try_json_loads(c)
        if obj is not None:
            return obj

    # 3) common fixes: remove trailing commas before } or ]
    cleaned = re.sub(r",\s*(\]|\})", r"\1", text)
    obj = try_json_loads(cleaned)
    if obj is not None:
        return obj

    # 4) replace single quotes with double quotes (careful)
    cleaned2 = re.sub(r"'", r'"', cleaned)
    obj = try_json_loads(cleaned2)
    if obj is not None:
        return obj

    # 5) remove leading non-json junk until first { or [
    first = min((i for i in [text.find("["), text.find("{")] if i>=0), default=-1)
    if first > 0:
        attempt = text[first:]
        obj = try_json_loads(attempt)
        if obj is not None:
            return obj

    # 6) give up (caller will handle)
    raise ValueError("Failed to extract JSON from model output.")

# --- core generation with retries ---
def _call_model(prompt, retries=2, sleep=1.0):
    for attempt in range(1, retries+1):
        model = genai.GenerativeModel(MODEL)
        resp = model.generate_content(prompt)
        raw = resp.text or ""
        if raw.strip():
            return raw
        if attempt < retries:
            time.sleep(sleep)
    return raw

def generate_mcqs(level, difficulty, count=15, max_attempts=4):
    prompt = MCQ_PROMPT.format(
        count=count,
        difficulty=difficulty,
        round_name=level
    )

    attempts = 0
    while attempts < max_attempts:
        attempts += 1
        raw = _call_model(prompt, retries=2)
        debug_file = write_raw_debug(level, difficulty, raw)
        try:
            mcqs = extract_json(raw)
            # basic validation: should be a list of length count
            if not isinstance(mcqs, list):
                raise ValueError("Parsed JSON is not a list.")
            if len(mcqs) != count:
                # Accept if model returned count but not exact — but prefer exact
                print(f"⚠ Warning: expected {count} items but got {len(mcqs)} (attempt {attempts})")
            # save and return
            save(level, difficulty, mcqs)
            return mcqs
        except Exception as e:
            print(f"⚠ JSON parse attempt {attempts} failed: {e}. raw saved to {debug_file}")
            # small backoff
            time.sleep(0.8 * attempts)

    raise RuntimeError(f"Failed to generate valid MCQs for {level} after {max_attempts} attempts. See debug_output/ for raw outputs.")

def generate_coding_question(difficulty, max_attempts=4):
    prompt = CODING_PROMPT.format(difficulty=difficulty)

    attempts = 0
    while attempts < max_attempts:
        attempts += 1
        raw = _call_model(prompt, retries=2)
        debug_file = write_raw_debug("L4_coding", difficulty, raw)
        try:
            obj = extract_json(raw)
            # ensure it's an object / dict
            if isinstance(obj, list):
                if len(obj) == 1 and isinstance(obj[0], dict):
                    obj = obj[0]
                else:
                    raise ValueError("Coding prompt returned a list instead of a single object.")
            if not isinstance(obj, dict):
                raise ValueError("Parsed coding JSON is not an object.")
            save("L4", difficulty, [obj])
            return obj
        except Exception as e:
            print(f"⚠ JSON parse attempt {attempts} failed: {e}. raw saved to {debug_file}")
            time.sleep(0.8 * attempts)

    raise RuntimeError(f"Failed to generate valid coding question after {max_attempts} attempts. See debug_output/ for raw outputs.")
