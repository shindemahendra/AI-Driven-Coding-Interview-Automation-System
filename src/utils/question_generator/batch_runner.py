import time
from .generator import generate_mcqs, generate_coding_question

def generate_full_set(difficulty):
    print(f"\n🌟 Generating full question sets for difficulty: {difficulty}\n")

    print("=== L1 ===")
    generate_mcqs("L1", difficulty, 15)
    time.sleep(6)

    print("\n=== L2 ===")
    generate_mcqs("L2", difficulty, 15)
    time.sleep(6)

    print("\n=== L3 ===")
    generate_mcqs("L3", difficulty, 15)
    time.sleep(6)

    print("\n=== L4 (Coding) ===")
    generate_coding_question(difficulty)
    time.sleep(6)

    print("\n=== L5 ===")
    generate_mcqs("L5", difficulty, 15)
    time.sleep(6)

    print("\n🎉 All questions generated successfully!\n")
