import json
import os

from src.utils.google_forms.create_form_mcq import create_mcq_form
from src.utils.google_forms.html_wrapper import generate_timed_html

# ==========================
# CONFIGURATION
# ==========================

TIMER_MINUTES = 20
OUTPUT_DIR = "timed_forms"


def create_all_google_forms(json_path):

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(json_path, "r") as f:
        data = json.load(f)

    candidate = data["candidate"]
    candidate_uid = candidate["uid"]

    print("\n===============================")
    print(f" Creating Google Forms for {candidate_uid}")
    print("===============================\n")

    form_ids = {}

    # ---- L1 ----
    print("🔵 Creating L1 Form...")
    form_ids["L1"] = create_mcq_form("L1", candidate_uid, data["L1"])
    generate_timed_html(
        form_id=form_ids["L1"],
        minutes=TIMER_MINUTES,
        output_path=f"{OUTPUT_DIR}/{candidate_uid}_L1_timed.html",
        title=f"{candidate_uid} - L1 Timed Test"
    )

    # ---- L2 ----
    print("🔵 Creating L2 Form...")
    form_ids["L2"] = create_mcq_form("L2", candidate_uid, data["L2"])
    generate_timed_html(
        form_id=form_ids["L2"],
        minutes=TIMER_MINUTES,
        output_path=f"{OUTPUT_DIR}/{candidate_uid}_L2_timed.html",
        title=f"{candidate_uid} - L2 Timed Test"
    )

    # ---- L3 ----
    print("🔵 Creating L3 Form...")
    form_ids["L3"] = create_mcq_form("L3", candidate_uid, data["L3"])
    generate_timed_html(
        form_id=form_ids["L3"],
        minutes=TIMER_MINUTES,
        output_path=f"{OUTPUT_DIR}/{candidate_uid}_L3_timed.html",
        title=f"{candidate_uid} - L3 Timed Test"
    )

    # ---- L5 ----
    print("🔵 Creating L5 Form...")
    form_ids["L5"] = create_mcq_form("L5", candidate_uid, data["L5"])
    generate_timed_html(
        form_id=form_ids["L5"],
        minutes=TIMER_MINUTES,
        output_path=f"{OUTPUT_DIR}/{candidate_uid}_L5_timed.html",
        title=f"{candidate_uid} - L5 Timed Test"
    )

    # ❌ REMOVE L4 FORM CREATION
    print("🟣 L4 Google Form Skipped (Using Localhost Coding Server Instead)")

    print("\n🎉 ALL MCQ GOOGLE FORMS CREATED!")
    return form_ids
