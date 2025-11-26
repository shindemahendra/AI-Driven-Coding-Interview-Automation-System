from src.utils.google_forms.form_api import get_forms_service

def clean(text):
    if not text:
        return ""
    return " ".join(str(text).splitlines()).strip()


def update_form_with_mcqs(form_id, questions):
    service = get_forms_service()

    requests = []

    for q in questions:
        question_text = clean(q["question"])
        options = [clean(opt) for opt in q["options"]]
        correct = clean(q.get("correct_answer") or q.get("answer") or "")

        # Create MCQ item
        item_request = {
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
                "location": {"index": 0}
            }
        }

        requests.append(item_request)

    # Add all MCQ items
    service.forms().batchUpdate(
        formId=form_id,
        body={"requests": requests}
    ).execute()


def update_form_with_coding(form_id, coding_question):
    service = get_forms_service()

    title = clean(coding_question["problem"])
    description = (
        f"Input:\n{coding_question['input']}\n\n"
        f"Expected Output:\n{coding_question['output']}"
    )

    request = {
        "requests": [
            {
                "createItem": {
                    "item": {
                        "title": title,
                        "description": description,
                        "questionItem": {
                            "question": {
                                "required": True,
                                "textQuestion": {"paragraph": True}
                            }
                        }
                    },
                    "location": {"index": 0}
                }
            }
        ]
    }

    service.forms().batchUpdate(formId=form_id, body=request).execute()
