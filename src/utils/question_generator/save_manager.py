# src/utils/question_generator/save_manager.py

import os, json, hashlib, datetime

BANK_DIR = "question_bank"


def ensure_dir(path=None):
    if path:
        os.makedirs(path, exist_ok=True)
    else:
        os.makedirs(BANK_DIR, exist_ok=True)


def q_hash(text: str):
    return hashlib.md5(text.lower().strip().encode()).hexdigest()


def load(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []


def save(level, difficulty, questions):
    ensure_dir()

    # 1. Main file (always overwritten with latest)
    filename = f"{level}_{difficulty}.json"
    path = os.path.join(BANK_DIR, filename)

    # 2. Versioned folder
    version_folder = os.path.join(BANK_DIR, f"{level}_{difficulty}_history")
    ensure_dir(version_folder)

    # 3. Timestamped version file
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    version_file = os.path.join(version_folder, f"{level}_{difficulty}_{timestamp}.json")

    # Always save full new data to main file
    with open(path, "w") as f:
        json.dump(questions, f, indent=4)

    # Also save a snapshot to history folder
    with open(version_file, "w") as f:
        json.dump(questions, f, indent=4)

    print(f"✔ Saved latest → {path}")
    print(f"✔ Version archived → {version_file}")
