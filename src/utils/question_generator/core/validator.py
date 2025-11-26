import json
import re

def extract_json(raw_text: str):
    """
    Extracts the FIRST valid top-level JSON array from Gemini output.
    Handles messy output, comments, text before/after JSON.
    """
    # Find the first '[' and last ']'
    start = raw_text.find('[')
    end = raw_text.rfind(']')

    if start == -1 or end == -1:
        raise ValueError("No JSON array found in text.")

    json_str = raw_text[start:end+1]

    # Remove trailing commas
    json_str = re.sub(r",\s*]", "]", json_str)

    try:
        data = json.loads(json_str)
    except Exception as e:
        raise ValueError(f"Invalid JSON after cleanup: {e}")

    # Flatten nested lists
    flat = []
    for item in data:
        if isinstance(item, list):
            flat.extend(item)
        else:
            flat.append(item)

    return flat
