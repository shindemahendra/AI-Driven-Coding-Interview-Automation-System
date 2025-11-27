from src.utils.question_generator.pick_random_questions import generate_candidate_test


def run_candidate_test_generation(full_name: str, email: str, difficulty: str):
    """
    Runs the candidate test generation process using inputs provided by an external system
    (like a Streamlit dashboard).
    """
    print(f"\n===== Generating Test for {full_name} ({difficulty}) =====\n")

    # NOTE: The function 'generate_candidate_test' must be defined
    # in 'src/utils/question_generator/pick_random_questions.py' for this script to run.
    generate_candidate_test(full_name, email, difficulty)

    print(f"\n🎉 Candidate Test JSON Generated for {full_name}!")


if __name__ == "__main__":
    # This block allows the script to be run directly from the command line for testing/CLI usage.
    print("\n===== Candidate Test Generator (CLI) =====\n")

    full_name = input("Enter Full Name: ").strip()
    email = input("Enter Email: ").strip()
    difficulty = input("Enter difficulty (easy / medium / hard): ").strip().lower()

    run_candidate_test_generation(full_name, email, difficulty)