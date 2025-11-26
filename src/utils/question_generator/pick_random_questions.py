import os
import json
import random
from src.utils.question_generator.uid_helper import generate_uid

MASTER_DIR = "question_bank/master"
TEST_DIR = "question_bank/tests"

os.makedirs(TEST_DIR, exist_ok=True)

def pick_questions_from_master(level, difficulty, count):
    file_path = f"{MASTER_DIR}/{level}_{difficulty}_master.json"

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Master bank missing: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        bank = json.load(f)

    return random.sample(bank, count)


def generate_candidate_test(full_name, email, difficulty):
    uid = generate_uid(full_name)

    print(f"\nGenerating test for: {full_name} ({difficulty})")
    print(f"UID → {uid}")

    test = {
        "candidate": {
            "name": full_name,
            "email": email,
            "uid": uid,
            "difficulty": difficulty
        }
    }

    # L1, L2, L3, L5 → MCQ (15 each)
    for level in ["L1", "L2", "L3", "L5"]:
        test[level] = pick_questions_from_master(level, difficulty, 15)

    # L4 → Coding (1)
    test["L4"] = pick_questions_from_master("L4", difficulty, 1)

    # Save file
    output_file = f"{TEST_DIR}/{uid}_{difficulty}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(test, f, indent=4)

    print(f"✔ Test created → {output_file}")
    return output_file
