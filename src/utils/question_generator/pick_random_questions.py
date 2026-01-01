# src/utils/question_generator/pick_random_questions.py

"""
Question selection & per-candidate test generation.

SUPPORTS:
- Legacy difficulty + domain based generation (DO NOT BREAK)
- New ROLE based generation with optional domain round
- L4 coding round is NOT handled here

THIS FILE IS THE ONLY PLACE that reads:
- ROLE_TO_TEST_CONFIG
"""

import os
import json
import random
from typing import Dict, List, Tuple

from src.utils.question_generator.uid_helper import generate_uid
from src.utils.question_generator.role_config import ROLE_TO_TEST_CONFIG

# -------------------------------------------------
# PATHS
# -------------------------------------------------
MASTER_DIR = "question_bank/master"
TEST_DIR = "question_bank/tests"

os.makedirs(TEST_DIR, exist_ok=True)

# -------------------------------------------------
# CONSTANTS
# -------------------------------------------------
QUESTIONS_PER_ROUND = 15

DOMAIN_ROUND_MAP = {
    "storage": "L5_storage-master_questions.json",
    "virtualization": "L5_virtualisation_master_questions.json",
    "networking": "L5_networking_master_questions.json",
}

# -------------------------------------------------
# LOW-LEVEL HELPERS
# -------------------------------------------------
def _load_master_questions(filename: str) -> List[dict]:
    path = os.path.join(MASTER_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Master question file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if len(data) < QUESTIONS_PER_ROUND:
        raise ValueError(
            f"Not enough questions in {filename}. "
            f"Required={QUESTIONS_PER_ROUND}, Found={len(data)}"
        )

    return data


def _pick_random_questions(filename: str) -> List[dict]:
    bank = _load_master_questions(filename)
    return random.sample(bank, QUESTIONS_PER_ROUND)


# -------------------------------------------------
# NEW: ROLE-BASED GENERATION (PRIMARY)
# -------------------------------------------------
def generate_candidate_test_by_role(
    full_name: str,
    email: str,
    role_key: str,
    domain: str | None = None,
) -> Tuple[str, str]:
    """
    Generate candidate test JSON using ROLE configuration.

    Returns:
        (uid, json_path)
    """

    if role_key not in ROLE_TO_TEST_CONFIG:
        raise ValueError(f"Invalid role key: {role_key}")

    role_cfg = ROLE_TO_TEST_CONFIG[role_key]

    uid = generate_uid(full_name)

    test_data: Dict[str, list] = {
        "candidate": {
            "name": full_name,
            "email": email,
            "uid": uid,
            "role": role_key,
        }
    }

    for level, source in role_cfg.items():

        # ---------------- L4 (CODING) ----------------
        if source == "coding":
            continue  # handled elsewhere

        # ---------------- DOMAIN OPTIONAL ----------------
        if source == "domain_optional":
            if not domain:
                continue

            domain = domain.lower()
            if domain not in DOMAIN_ROUND_MAP:
                raise ValueError(f"Invalid domain: {domain}")

            filename = DOMAIN_ROUND_MAP[domain]

        # ---------------- NORMAL MCQ ----------------
        else:
            filename = source

        test_data[level] = _pick_random_questions(filename)

    json_path = os.path.join(TEST_DIR, f"{uid}_role.json")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(test_data, f, indent=4)

    return uid, json_path


# -------------------------------------------------
# LEGACY: DIFFICULTY + DOMAIN BASED (DO NOT REMOVE)
# -------------------------------------------------
def generate_candidate_test(
    full_name: str,
    email: str,
    difficulty: str,
    domain: str,
) -> Tuple[str, str]:
    """
    ⚠️ LEGACY FLOW (kept for backward compatibility)

    Uses files like:
    L1_easy_master.json
    L2_medium_master.json
    etc.
    """

    difficulty = difficulty.lower().strip()
    domain = domain.lower().strip()

    uid = generate_uid(full_name)

    test_data = {
        "candidate": {
            "name": full_name,
            "email": email,
            "uid": uid,
            "difficulty": difficulty,
            "domain": domain,
        }
    }

    LEVEL_COUNTS = {
        "L1": 15,
        "L2": 15,
        "L3": 15,
        "L5": 15,
    }

    for level, count in LEVEL_COUNTS.items():
        suffix = ""

        if level in ["L2", "L3"] and domain in ["js", "javascript"]:
            suffix = "_js"

        filename = f"{level}_{difficulty}{suffix}_master.json"
        test_data[level] = random.sample(
            _load_master_questions(filename), count
        )

    json_path = os.path.join(TEST_DIR, f"{uid}_{difficulty}.json")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(test_data, f, indent=4)

    return uid, json_path
