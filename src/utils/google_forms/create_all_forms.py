import json
import os

from src.utils.google_forms.create_form_mcq import create_mcq_form
from src.utils.google_forms.create_form_coding import create_coding_form
from src.utils.google_forms.html_wrapper import generate_timed_html


# ==========================
# CONFIGURATION
# ==========================

TIMER_MINUTES = 20              # Default countdown timer
OUTPUT_DIR = "timed_forms"      # Folder for HTML output


def create_all_google_forms(json_path):

    # Create output folder if missing
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load test specification JSON
    with open(json_path, "r") as f:
        data = json.load(f)

    candidate = data["candidate"]
    candidate_uid = candidate["uid"]

    print("\n===============================")
    print(f" Creating Google Forms for {candidate_uid}")
    print("===============================\n")

    # Store each created form's ID
    form_ids = {}

    # -------------------------
    # L1
    # -------------------------
    print("🔵 Creating L1 Form...")
    form_ids["L1"] = create_mcq_form("L1", candidate_uid, data["L1"])

    generate_timed_html(
        form_id=form_ids["L1"],
        minutes=TIMER_MINUTES,
        output_path=f"{OUTPUT_DIR}/{candidate_uid}_L1_timed.html",
        title=f"{candidate_uid} - L1 Timed Test"
    )

    # -------------------------
    # L2
    # -------------------------
    print("🔵 Creating L2 Form...")
    form_ids["L2"] = create_mcq_form("L2", candidate_uid, data["L2"])

    generate_timed_html(
        form_id=form_ids["L2"],
        minutes=TIMER_MINUTES,
        output_path=f"{OUTPUT_DIR}/{candidate_uid}_L2_timed.html",
        title=f"{candidate_uid} - L2 Timed Test"
    )

    # -------------------------
    # L3
    # -------------------------
    print("🔵 Creating L3 Form...")
    form_ids["L3"] = create_mcq_form("L3", candidate_uid, data["L3"])

    generate_timed_html(
        form_id=form_ids["L3"],
        minutes=TIMER_MINUTES,
        output_path=f"{OUTPUT_DIR}/{candidate_uid}_L3_timed.html",
        title=f"{candidate_uid} - L3 Timed Test"
    )

    # -------------------------
    # L5
    # -------------------------
    print("🔵 Creating L5 Form...")
    form_ids["L5"] = create_mcq_form("L5", candidate_uid, data["L5"])

    generate_timed_html(
        form_id=form_ids["L5"],
        minutes=TIMER_MINUTES,
        output_path=f"{OUTPUT_DIR}/{candidate_uid}_L5_timed.html",
        title=f"{candidate_uid} - L5 Timed Test"
    )

    # -------------------------
    # L4 (coding) – optional
    # -------------------------
    if "L4" in data and len(data["L4"]) > 0:
        print("🟣 Creating L4 Coding Form...")
        try:
            form_ids["L4"] = create_coding_form(candidate_uid, data["L4"][0])

            generate_timed_html(
                form_id=form_ids["L4"],
                minutes=TIMER_MINUTES,
                output_path=f"{OUTPUT_DIR}/{candidate_uid}_L4_timed.html",
                title=f"{candidate_uid} - L4 Coding Test"
            )

        except Exception as e:
            print(f"⚠ L4 skipped: {e}")

    # -------------------------
    # DONE
    # -------------------------

    print("\n🎉 ALL GOOGLE FORMS CREATED!")
    print("Generated Google Form IDs:\n")
    print(json.dumps({"forms": form_ids}, indent=4))

    print("\n🔗 EDIT LINKS (ADMIN ONLY):")
    for level, form_id in form_ids.items():
        print(f"{level}: https://docs.google.com/forms/d/{form_id}/edit")

    print("\n⏱ TIMED TEST LINKS (SHARE WITH CANDIDATE):")
    for level in form_ids:
        html_file = f"{candidate_uid}_{level}_timed.html"
        print(f"{level}: {OUTPUT_DIR}/{html_file}")

    return form_ids


if __name__ == "__main__":
    path = "question_bank/tests/rbodicherla_easy.json"
    create_all_google_forms(path)
