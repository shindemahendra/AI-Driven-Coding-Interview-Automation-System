from src.utils.google_forms.form_api import get_forms_service

def clean(text):
    if not text:
        return ""
    return " ".join(str(text).splitlines()).strip()

def create_coding_form(candidate_uid, q):
    service = get_forms_service()

    form_title = f"L4 Coding Test for {candidate_uid}"

    # Create form with only a title
    created = service.forms().create(
        body={"info": {"title": form_title}}
    ).execute()

    form_id = created["formId"]

    # Prepare safe fields
    title = clean(q.get("title", "Coding Problem"))
    desc = clean(q.get("description", ""))
    input_fmt = clean(q.get("input_format", ""))
    output_fmt = clean(q.get("output_format", ""))
    constraints = clean(q.get("constraints", ""))
    sample_in = clean(q.get("sample_input", ""))
    sample_out = clean(q.get("sample_output", ""))

    full_description = (
        f"{desc}\n\n"
        f"Input Format:\n{input_fmt}\n\n"
        f"Output Format:\n{output_fmt}\n\n"
        f"Constraints:\n{constraints}\n\n"
        f"Sample Input:\n{sample_in}\n\n"
        f"Sample Output:\n{sample_out}"
    )

    requests = [
        {
            "createItem": {
                "item": {
                    "title": title,
                    "description": full_description,
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

    service.forms().batchUpdate(
        formId=form_id,
        body={"requests": requests}
    ).execute()

    print(f"✔ L4 coding form created: https://docs.google.com/forms/d/{form_id}/edit")
    return form_id
