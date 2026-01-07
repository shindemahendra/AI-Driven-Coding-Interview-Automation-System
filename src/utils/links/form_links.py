def build_form_url(value: str) -> str:
    """
    SINGLE SOURCE OF TRUTH for MCQ links.

    - If already full URL → return as-is
    - If form ID → convert to Google Form URL
    """

    if not value:
        return ""

    value = value.strip()

    if value.startswith("http://") or value.startswith("https://"):
        return value

    # Google Form ID → FULL URL
    return f"https://docs.google.com/forms/d/e/{value}/viewform"
