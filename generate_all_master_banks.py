from src.utils.question_generator.master_bank.generate_master_bank import generate_master

levels = ["L1", "L2", "L3", "L5"]  # Excluding L4 for now
difficulties = ["easy", "medium", "hard"]

for level in levels:
    for difficulty in difficulties:
        count = 100  # always generate 100 MCQs per level & difficulty
        print(f"\n=== START {level} - {difficulty} ===")
        generate_master(level, difficulty, count)

print("\nAll master banks generated successfully!")
