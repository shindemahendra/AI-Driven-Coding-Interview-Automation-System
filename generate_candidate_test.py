from src.utils.question_generator.pick_random_questions import generate_candidate_test as _generate_candidate_test


def run_candidate_test_generation(full_name: str, email: str, difficulty: str):
    """
    Wrapper used by UI (Streamlit) or CLI.

    Returns:
        (uid, json_path)
    """
    uid, json_path = _generate_candidate_test(full_name, email, difficulty)
    return uid, json_path


if __name__ == "__main__":
    print("\n===== Candidate Test Generator (CLI) =====\n")

    full_name = input("Enter Full Name: ").strip()
    email = input("Enter Email: ").strip()
    difficulty = input("Enter difficulty (easy / medium / hard): ").strip().lower()

    uid, json_path = run_candidate_test_generation(full_name, email, difficulty)

    print(f"\n🎉 Candidate Test JSON Generated!")
    print(f"UID      : {uid}")
    print(f"JSON Path: {json_path}")
