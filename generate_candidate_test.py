"""
generate_candidate_test.py
FINAL – STABLE – DO NOT REFACTOR
"""

from src.utils.question_generator.role_config import ROLE_TO_TEST_CONFIG
from src.utils.question_generator.pick_random_questions import (
    generate_candidate_test_by_role,
    generate_candidate_test as generate_candidate_test_legacy,
)

# ----------------------------
# NEW ROLE-BASED (PRIMARY)
# ----------------------------
def run_candidate_test_generation_by_role(
    full_name: str,
    email: str,
    role_key: str,
    domain: str | None = None,
):
    if role_key not in ROLE_TO_TEST_CONFIG:
        raise ValueError(f"Invalid role key: {role_key}")

    return generate_candidate_test_by_role(
        full_name=full_name,
        email=email,
        role_key=role_key,
        domain=domain,
    )


# ----------------------------
# LEGACY (DO NOT REMOVE)
# ----------------------------
def run_candidate_test_generation(
    full_name: str,
    email: str,
    difficulty: str,
    domain: str,
):
    return generate_candidate_test_legacy(
        full_name=full_name,
        email=email,
        difficulty=difficulty,
        domain=domain,
    )

# =============================================================
# CLI SUPPORT (OPTIONAL, SAFE)
# =============================================================
if __name__ == "__main__":
    print("\n===== Candidate Test Generator (CLI) =====\n")

    mode = input(
        "Choose mode:\n"
        "1 → Role based (recommended)\n"
        "2 → Difficulty based (legacy)\n"
        "Enter choice (1/2): "
    ).strip()

    full_name = input("Enter Full Name: ").strip()
    email = input("Enter Email: ").strip()

    if mode == "1":
        role_key = input(
            "Enter role key (example: python_entry, java_qa, python_dev): "
        ).strip()

        domain = input(
            "Enter domain (storage / virtualization / networking) or press Enter to skip: "
        ).strip()
        domain = domain if domain else None

        uid, json_path = run_candidate_test_generation_by_role(
            full_name=full_name,
            email=email,
            role_key=role_key,
            domain=domain,
        )

    else:
        difficulty = input("Enter difficulty (easy / medium / hard): ").strip()
        domain = input("Enter domain: ").strip()

        uid, json_path = run_candidate_test_generation(
            full_name=full_name,
            email=email,
            difficulty=difficulty,
            domain=domain,
        )

    print("\n🎉 Candidate Test JSON Generated Successfully!")
    print(f"UID      : {uid}")
    print(f"JSON Path: {json_path}")
