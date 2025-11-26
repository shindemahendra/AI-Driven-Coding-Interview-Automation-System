# main.py

from src.utils.question_generator.batch_runner import generate_full_set

if __name__ == "__main__":
    difficulty = input("Enter difficulty (easy / medium / hard): ").strip().lower()
    generate_full_set(difficulty)
