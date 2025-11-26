from googleapiclient.discovery import build
from src.utils.sheet_reader_oauth import get_credentials
from src.utils.google_forms.link_sheet import attach_sheet_to_form


def create_sheet(title):
    creds = get_credentials()
    sheet_service = build("sheets", "v4", credentials=creds)

    body = {"properties": {"title": title}}
    sheet = sheet_service.spreadsheets().create(body=body).execute()

    sheet_id = sheet["spreadsheetId"]
    print(f"✔ Created sheet: {title} → {sheet_id}")
    return sheet_id


def auto_link_forms(form_ids, candidate_uid):
    sheets = {}

    for level, form_id in form_ids.items():
        title = f"{candidate_uid}_{level}_responses"
        sheet_id = create_sheet(title)
        attach_sheet_to_form(form_id, sheet_id)
        sheets[level] = sheet_id

    return sheets


if __name__ == "__main__":
    # Example usage
    form_ids = {
        "L1": input("Enter L1 formId: "),
        "L2": input("Enter L2 formId: "),
        "L3": input("Enter L3 formId: "),
        "L5": input("Enter L5 formId: "),
    }

    candidate = input("Candidate UID: ")

    auto_link_forms(form_ids, candidate)
