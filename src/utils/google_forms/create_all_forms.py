import json
from src.utils.google_forms.form_templates import TEMPLATE_FORM_IDS
from src.utils.google_forms.form_api import get_drive_service
from src.utils.google_forms.update_form_questions import (
    update_form_with_mcqs,
    update_form_with_coding,
)
from src.utils.question_generator.uid_helper import generate_uid


def duplicate_form(template_id, new_title):
    drive = get_drive_service()

    copied = drive.files().copy(
        fileId=template_id,
        body={"name": new_title}
    ).execute()

    return copied["id"]


def create_all_google_forms(json_path):
    # Load candidate data
    with open(json_path, "r") as f:
        data = json.load(f)

    candidate = data["candidate"]
    candidate_uid = candidate["uid"]

    print("\n===============================")
    print(f" Creating Google Forms for {candidate_uid}")
    print("===============================\n")

    form_ids = {}

    # ------------------------------------------------------
    # DUPLICATE TEMPLATES FOR EACH ROUND
    # ------------------------------------------------------
    for level in ["L1", "L2", "L3", "L5", "L4"]:
        print(f"📄 Duplicating {level} Template...")

        new_title = f"{candidate_uid}_{level}"
        form_ids[level] = duplicate_form(TEMPLATE_FORM_IDS[level], new_title)

        print(f"✔ Duplicated {level} → {form_ids[level]}")

    print("\n✔ All templates duplicated successfully\n")

    # ------------------------------------------------------
    # INSERT QUESTIONS INTO NEWLY CREATED FORMS
    # ------------------------------------------------------
    print("✏ Updating L1 Questions...")
    update_form_with_mcqs(form_ids["L1"], data["L1"])

    print("✏ Updating L2 Questions...")
    update_form_with_mcqs(form_ids["L2"], data["L2"])

    print("✏ Updating L3 Questions...")
    update_form_with_mcqs(form_ids["L3"], data["L3"])

    print("✏ Updating L5 Questions...")
    update_form_with_mcqs(form_ids["L5"], data["L5"])

    print("🟣 Skipping L4 (Coding) — JSON structure mismatch")

    # ------------------------------------------------------
    # PRINT RESULTS
    # ------------------------------------------------------
    print("\n🎉 ALL DONE!\nGenerated Forms:\n")
    for level, fid in form_ids.items():
        print(f"{level}: https://docs.google.com/forms/d/{fid}/edit")

    return form_ids


if __name__ == "__main__":
    path = "question_bank/tests/rbodicherla_easy.json"
    create_all_google_forms(path)
