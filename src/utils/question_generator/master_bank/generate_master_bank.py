import os, json
from src.utils.question_generator.levels.L1_logic import generate_L1_questions
from src.utils.question_generator.levels.L2_python import generate_L2_questions
from src.utils.question_generator.levels.L3_debug import generate_L3_questions
from src.utils.question_generator.levels.L4_coding import generate_L4_questions
from src.utils.question_generator.levels.L5_softskills import generate_L5_questions

MASTER_DIR = "question_bank/master"
os.makedirs(MASTER_DIR, exist_ok=True)

GEN_MAP = {
    "L1": generate_L1_questions,
    "L2": generate_L2_questions,
    "L3": generate_L3_questions,
    "L4": generate_L4_questions,
    "L5": generate_L5_questions,
}


def generate_master(level, difficulty, count):
    print(f"\n📌 Generating MASTER → {level}_{difficulty} ({count})")

    data = GEN_MAP[level](difficulty, count)

    if not isinstance(data, list):
        raise RuntimeError("Expected list of questions")

    out = f"{MASTER_DIR}/{level}_{difficulty}_master.json"
    with open(out, "w") as f:
        json.dump(data, f, indent=4)

    print(f"✔ Saved → {out}")
