import os
import json
from .generator import generate_mcqs, generate_coding_question

MASTER_DIR = "question_bank/master"


def ensure_dir():
    os.makedirs(MASTER_DIR, exist_ok=True)


def generate_master_bank(level, difficulty, count):
    ensure_dir()

    file_path = f"{MASTER_DIR}/{level}_{difficulty}_master.json"

    print(f"\n🔵 Generating MASTER BANK for {level.upper()} ({difficulty})...")
    print(f"Target: {count} questions")

    # For coding round
    if level == "L4":
        questions = []
        for i in range(count):
            print(f" → Generating coding Q{i+1}/{count}")
            q = generate_coding_question(difficulty)
            questions.append(q)
        with open(file_path, "w") as f:
            json.dump(questions, f, indent=4)
        print(f"✔ Saved master bank → {file_path}")
        return

    # For MCQ rounds
    questions = []
    batch_size = 20  # Generate smaller chunks
    needed_batches = count // batch_size

    for batch in range(needed_batches):
        print(f" → Batch {batch+1}/{needed_batches}")
        mcqs = generate_mcqs(level, difficulty, batch_size)
        questions.extend(mcqs)

    with open(file_path, "w") as f:
        json.dump(questions, f, indent=4)

    print(f"✔ Saved master bank → {file_path}")
