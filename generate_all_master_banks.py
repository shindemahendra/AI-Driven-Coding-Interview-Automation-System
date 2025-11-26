from src.utils.question_generator.master_bank.generate_master_bank import generate_master

levels = ["L1", "L2", "L3", "L4", "L5"]
difficulty = "easy"

for level in levels:
    count = 100 if level != "L4" else 20
    generate_master(level, difficulty, count)
