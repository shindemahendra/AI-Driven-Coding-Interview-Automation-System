# src/utils/question_generator/core/validator.py

import json
import re

def extract_json(raw_text: str):
    """
    Extracts JSON array from Gemini response by cleaning common errors.
    Handles:
    - text before/after JSON
    - invalid escape sequences
    - trailing commas
    - nested list wrapping
    """

    # Try to locate first JSON array block
    start = raw_text.find('[')
    end = raw_text.rfind(']')

    if start == -1 or end == -1:
        raise ValueError("❌ No JSON array detected in response.")

    json_str = raw_text[start:end+1]

    # Fix invalid escape characters like "\("
    json_str = re.sub(r'\\(?!["\\/bfnrt])', '', json_str)

    # Remove trailing commas before `]`
    json_str = re.sub(r",\s*]", "]", json_str)

    # Remove trailing commas before `}`
    json_str = re.sub(r",\s*}", "}", json_str)

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"❌ JSON still invalid after cleanup: {e}")

    flat = []
    for item in data:
        if isinstance(item, list):
            flat.extend(item)
        else:
            flat.append(item)

    return flat
