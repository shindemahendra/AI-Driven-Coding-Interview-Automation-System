# src/utils/google_forms/create_form_mcq.py

from src.utils.google_forms.form_api import get_forms_service


def _dedupe_options(options):
    """
    Remove duplicate options while preserving order.
    Also trims whitespace to avoid Google Forms rejection.
    """
    seen = set()
    clean = []

    for opt in options:
        val = str(opt).strip()
        if val.lower() not in seen:
            seen.add(val.lower())
            clean.append(val)

    return clean


def create_mcq_form(level: str, candidate_uid: str, questions: list):
    """
    Create a Google Form MCQ safely.
    - Deduplicates options per question
    - Prevents Google Forms API 400 errors
    """

    forms_service = get_forms_service()

    # -------------------------------------------------
    # CREATE FORM
    # -------------------------------------------------
    form = (
        forms_service.forms()
        .create(
            body={
                "info": {
                    "title": f"{candidate_uid} - {level} MCQ Test",
                }
            }
        )
        .execute()
    )

    form_id = form["formId"]

    requests = []

    for idx, q in enumerate(questions):
        raw_options = q.get("options", [])

        # ✅ CRITICAL FIX HERE
        options = _dedupe_options(raw_options)

        # Safety fallback (Google requires >= 2 options)
        if len(options) < 2:
            continue

        requests.append(
            {
                "createItem": {
                    "item": {
                        "title": q["question"],
                        "questionItem": {
                            "question": {
                                "required": True,
                                "choiceQuestion": {
                                    "type": "RADIO",
                                    "options": [
                                        {"value": opt} for opt in options
                                    ],
                                },
                            }
                        },
                    },
                    "location": {"index": idx},
                }
            }
        )

    # -------------------------------------------------
    # APPLY BATCH UPDATE
    # -------------------------------------------------
    if requests:
        forms_service.forms().batchUpdate(
            formId=form_id,
            body={"requests": requests},
        ).execute()

    return form_id
