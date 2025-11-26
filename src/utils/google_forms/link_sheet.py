from googleapiclient.discovery import build
from src.utils.sheet_reader_oauth import get_credentials

def attach_sheet_to_form(form_id, sheet_id):
    creds = get_credentials()
    service = build("forms", "v1", credentials=creds)

    body = {
        "destination": {
            "type": "SPREADSHEET",
            "spreadsheetId": sheet_id
        }
    }

    service.forms().setDestination(
        formId=form_id,
        body=body
    ).execute()

    print(f"✔ Linked form → sheet: {form_id} → {sheet_id}")
