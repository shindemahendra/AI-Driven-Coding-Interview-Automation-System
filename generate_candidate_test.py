from src.utils.question_generator.pick_random_questions import generate_candidate_test

if __name__ == "__main__":
    print("\n===== Candidate Test Generator =====\n")

    full_name = input("Enter Full Name: ").strip()
    email = input("Enter Email: ").strip()
    difficulty = input("Enter difficulty (easy / medium / hard): ").strip().lower()

    generate_candidate_test(full_name, email, difficulty)

    print("\n🎉 Candidate Test JSON Generated!")
