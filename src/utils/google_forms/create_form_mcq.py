# src/utils/google_forms/create_form_mcq.py

from src.utils.google_forms.form_api import get_forms_service


def _clean_text(text: str) -> str:
    """
    Google Forms does NOT allow newlines.
    This function:
    - Removes \n and \r
    - Collapses extra spaces
    """
    if not text:
        return ""

    return " ".join(str(text).replace("\n", " ").replace("\r", " ").split())


def _dedupe_and_clean_options(options):
    """
    - Remove duplicate options (case-insensitive)
    - Remove newlines
    - Preserve order
    """
    seen = set()
    clean = []

    for opt in options:
        val = _clean_text(opt)
        key = val.lower()

        if key and key not in seen:
            seen.add(key)
            clean.append(val)

    return clean


def create_mcq_form(level: str, candidate_uid: str, questions: list):
    """
    SAFE Google Form MCQ creation:
    - Removes duplicate options
    - Removes newlines
    - Prevents Google Forms 400 errors
    - RETURNS PUBLIC RESPONDER URL (CRITICAL FIX)
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

    # ✅ CRITICAL LINE (DO NOT REMOVE)
    responder_uri = form["responderUri"]

    requests = []

    for idx, q in enumerate(questions):
        question_text = _clean_text(q.get("question", ""))
        raw_options = q.get("options", [])

        options = _dedupe_and_clean_options(raw_options)

        # Google requires at least 2 options
        if not question_text or len(options) < 2:
            continue

        requests.append(
            {
                "createItem": {
                    "item": {
                        "title": question_text,
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
    # APPLY UPDATE
    # -------------------------------------------------
    if requests:
        forms_service.forms().batchUpdate(
            formId=form_id,
            body={"requests": requests},
        ).execute()

    # ✅ RETURN PUBLIC URL (NOT form_id)
    return {
        "form_id": form_id,
        "responder_url": responder_uri
    }

