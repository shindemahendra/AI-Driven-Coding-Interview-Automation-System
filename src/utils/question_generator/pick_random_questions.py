import os
import json
import random
from src.utils.question_generator.uid_helper import generate_uid

# Where your master banks live
MASTER_DIR = "question_bank/master"
# Where per-candidate tests will be stored
TEST_DIR = "question_bank/tests"

os.makedirs(TEST_DIR, exist_ok=True)

# How many questions per level
LEVEL_QUESTION_COUNTS = {
    "L1": 15,  # Logic MCQ
    "L2": 15,  # Python MCQ
    "L3": 15,  # Debugging / code MCQ
    "L5": 15,  # Soft skills MCQ
    "L4": 1,   # Coding round
}


def pick_questions_from_master(level: str, difficulty: str, count: int, domain: str):
    """
    Read the master bank JSON for given level+difficulty and domain, and randomly select `count` questions.

    If domain is 'js' or 'javascript' and level is L2 or L3, it looks for the '_js' suffix.

    Raises:
        FileNotFoundError if the master file does not exist
        ValueError if not enough questions in the bank
    """
    difficulty = difficulty.lower().strip()
    domain = domain.lower().strip()

    # Determine the domain suffix for L2 and L3
    domain_suffix = ""
    if level in ["L2", "L3"] and domain in ["js", "javascript"]:
        domain_suffix = "_js"
    # L4 is a coding round (repo), L1 and L5 are domain-agnostic.

    file_path = f"{MASTER_DIR}/{level}_{difficulty}{domain_suffix}_master.json"

    if not os.path.exists(file_path):
        # Provide context in the error message about the file path being sought
        raise FileNotFoundError(f"Master bank missing: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        bank = json.load(f)

    if len(bank) < count:
        raise ValueError(
            f"Not enough questions in {file_path}. "
            f"Required: {count}, Available: {len(bank)}"
        )

    return random.sample(bank, count)


def generate_candidate_test(full_name: str, email: str, difficulty: str, domain: str):
    """
    Generate a per-candidate full test JSON for ALL rounds (L1-L5) for the given difficulty.

    - Uses master banks: question_bank/master/L{n}_{difficulty}_master.json
    - Creates: question_bank/tests/{uid}_{difficulty}.json

    Returns:
        (uid, json_path)

    Raises:
        FileNotFoundError: if any required master bank file is missing
        ValueError: if any bank doesn't have enough questions
    """
    difficulty = difficulty.lower().strip()

    uid = generate_uid(full_name)
    print(f"\nGenerating test for: {full_name} ({difficulty})")
    print(f"UID → {uid}")

    test_data = {
        "candidate": {
            "name": full_name,
            "email": email,
            "uid": uid,
            "difficulty": difficulty,
        }
    }

    missing_files = []

    # Build test for all levels
    for level, q_count in LEVEL_QUESTION_COUNTS.items():
        try:
            selected_questions = pick_questions_from_master(level, difficulty, q_count, domain)
            test_data[level] = selected_questions
        except FileNotFoundError as e:
            missing_files.append(str(e))

    if missing_files:
        # If ANY master bank is missing → fail completely
        message = (
            f"Cannot generate test for difficulty '{difficulty}'.\n\n"
            f"The following master banks are missing:\n"
            + "\n".join(missing_files)
            + "\n\nPlease generate these master banks first."
        )
        raise FileNotFoundError(message)

    # Save per-candidate JSON
    json_path = f"{TEST_DIR}/{uid}_{difficulty}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(test_data, f, indent=4)

    print(f"✔ Test created → {json_path}")
    return uid, json_path
