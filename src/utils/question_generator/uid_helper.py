import re

def generate_uid(full_name: str) -> str:
    """
    Convert full name into unique id:
    Ravi Kumar Bodicherla → rbodicherla
    """
    parts = full_name.strip().lower().split()
    if len(parts) == 1:
        return parts[0]

    first_letter = parts[0][0]
    surname = parts[-1]
    uid = first_letter + surname

    return re.sub(r'[^a-z0-9]', '', uid)
