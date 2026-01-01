# /opt/interview_app/AI-Driven-Coding-Interview-Automation-System/src/utils/google_forms/create_all_forms.py

import json
import os

from src.utils.google_forms.create_form_mcq import create_mcq_form
from src.utils.google_forms.html_wrapper import generate_timed_html

# ==========================
# CONFIGURATION
# ==========================

TIMER_MINUTES = 20
OUTPUT_DIR = "timed_forms"

# MCQ rounds only (L4 is coding → skipped here)
MCQ_LEVEL_ORDER = ["L1", "L2", "L3", "L5", "L6"]


def create_all_google_forms(json_path):
    """
    Create Google Forms ONLY for MCQ rounds present in candidate JSON.
    - Safe for role-based configs
    - Safe for optional domain round
    - Does NOT assume L5 always exists
    - Does NOT touch L4
    """

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    candidate = data["candidate"]
    candidate_uid = candidate["uid"]

    print("\n===============================")
    print(f" Creating Google Forms for {candidate_uid}")
    print("===============================\n")

    form_ids = {}

    # ------------------------------------------------
    # CREATE MCQ FORMS (ONLY IF PRESENT)
    # ------------------------------------------------
    for level in MCQ_LEVEL_ORDER:
        if level not in data:
            print(f"⚪ Skipping {level} (not applicable for this role)")
            continue

        print(f"🔵 Creating {level} Form...")

        form_ids[level] = create_mcq_form(
            level,
            candidate_uid,
            data[level],
        )

        generate_timed_html(
            form_id=form_ids[level],
            minutes=TIMER_MINUTES,
            output_path=f"{OUTPUT_DIR}/{candidate_uid}_{level}_timed.html",
            title=f"{candidate_uid} - {level} Timed Test",
        )

    # ------------------------------------------------
    # L4 IS CODING ROUND (EXTERNAL SERVER)
    # ------------------------------------------------
    print("🟣 L4 Google Form Skipped (Using Coding Server Instead)")

    print("\n🎉 ALL APPLICABLE MCQ GOOGLE FORMS CREATED!")
    return form_ids
