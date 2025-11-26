from src.utils.google_forms.form_api import get_forms_service


def read_form_responses(form_id):
    service = get_forms_service()

    # Fetch submitted responses
    response = service.forms().responses().list(formId=form_id).execute()

    if "responses" not in response:
        print("❌ No responses found yet.")
        return

    print("======================================")
    print(f"📥 Responses for Form ID: {form_id}")
    print("======================================")

    for resp in response["responses"]:
        answer_map = resp.get("answers", {})
        print("\n📝 Submission:")
        for q_id, ans_obj in answer_map.items():
            text_answers = ans_obj.get("textAnswers", {}).get("answers", [])
            if text_answers:
                print(f"→ QID {q_id}: {text_answers[0]['value']}")
            else:
                print(f"→ QID {q_id}: No answer")


if __name__ == "__main__":
    # Put the latest L1 form ID here temporarily
    form_id = input("Enter Google Form ID: ")
    read_form_responses(form_id)
