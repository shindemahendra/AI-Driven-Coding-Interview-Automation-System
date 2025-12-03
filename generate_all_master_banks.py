from src.utils.question_generator.master_bank.generate_master_bank import generate_master

levels = ["L1", "L2", "L3", "L4", "L5"]
difficulties = ["easy", "medium", "hard"]

for level in levels:
    for difficulty in difficulties:
        count = 100 if level != "L4" else 20
        print(f"\n📌 Generating for {level} ({difficulty}) — count={count}")
        generate_master(level, difficulty, count)

print("\n🎉 All master banks generated successfully for all levels & difficulties!")
