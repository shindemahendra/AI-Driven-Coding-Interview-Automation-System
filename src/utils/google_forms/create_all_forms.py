import json
from src.utils.google_forms.create_form_mcq import create_mcq_form
from src.utils.google_forms.create_form_coding import create_coding_form


def create_all_google_forms(json_path):

    # Load candidate test JSON
    with open(json_path, "r") as f:
        data = json.load(f)

    candidate = data["candidate"]
    candidate_uid = candidate["uid"]

    print("\n===============================")
    print(f" Creating Google Forms for {candidate_uid}")
    print("===============================\n")

    # Store generated form IDs and URLs
    form_ids = {}

    # ------------------------------
    # L1 → MCQ
    # ------------------------------
    print("🔵 Creating L1 Form...")
    form_ids["L1"] = create_mcq_form("L1", candidate_uid, data["L1"])

    # ------------------------------
    # L2 → MCQ
    # ------------------------------
    print("🔵 Creating L2 Form...")
    form_ids["L2"] = create_mcq_form("L2", candidate_uid, data["L2"])

    # ------------------------------
    # L3 → MCQ
    # ------------------------------
    print("🔵 Creating L3 Form...")
    form_ids["L3"] = create_mcq_form("L3", candidate_uid, data["L3"])

    # ------------------------------
    # L5 → MCQ
    # ------------------------------
    print("🔵 Creating L5 Form...")
    form_ids["L5"] = create_mcq_form("L5", candidate_uid, data["L5"])

    # ------------------------------
    # OPTIONAL L4 CODING FORM
    # ------------------------------
    if "L4" in data and len(data["L4"]) > 0:
        print("🟣 Creating L4 Coding Form...")
        try:
            form_ids["L4"] = create_coding_form(candidate_uid, data["L4"][0])
        except Exception as e:
            print(f"⚠ L4 skipped: {e}")

    # --------------------------------------------------------
    # FINISHED — ONLY FORMS GENERATED
    # --------------------------------------------------------
    print("\n🎉 ALL GOOGLE FORMS CREATED SUCCESSFULLY!")
    print("Generated Form IDs:")
    print(json.dumps({"forms": form_ids}, indent=4))

    print("\n🔗 FORM LINKS:")

    for level, form_id in form_ids.items():
        print(f"{level}: https://docs.google.com/forms/d/{form_id}/edit")

    return form_ids


if __name__ == "__main__":
    path = "question_bank/tests/rbodicherla_easy.json"
    create_all_google_forms(path)