# src/utils/google_forms/create_form_mcq.py

from src.utils.google_forms.form_api import get_forms_service

def clean(text):
    if not text:
        return ""
    return " ".join(str(text).split()).strip()


def create_mcq_form(level, candidate_uid, questions):
    service = get_forms_service()

    # Create basic form
    created = service.forms().create(
        body={"info": {"title": f"{level} Test for {candidate_uid}"}}
    ).execute()

    form_id = created["formId"]

    requests = []

    for idx, q in enumerate(questions):

        question_text = clean(q.get("question", ""))
        options = [clean(opt) for opt in q.get("options", [])]

        requests.append({
            "createItem": {
                "item": {
                    "title": question_text,
                    "questionItem": {
                        "question": {
                            "required": True,
                            "choiceQuestion": {
                                "type": "RADIO",
                                "options": [{"value": opt} for opt in options],
                                "shuffle": True
                            }
                        }
                    }
                },
                "location": {"index": idx}
            }
        })

    # Make batch call to add all questions
    service.forms().batchUpdate(
        formId=form_id,
        body={"requests": requests}
    ).execute()

    print(f"✔ {level} form created: https://docs.google.com/forms/d/{form_id}/edit")
    return form_id
