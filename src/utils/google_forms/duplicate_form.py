from googleapiclient.discovery import build
from src.utils.sheet_reader_oauth import get_credentials


def duplicate_form(template_form_id: str, new_title: str) -> str:
    """
    Duplicate a Google Form using Drive API.
    Returns the new formId.
    """

    creds = get_credentials()
    drive = build("drive", "v3", credentials=creds)

    # 1️⃣ Copy the template file in Drive
    copied = drive.files().copy(
        fileId=template_form_id,
        body={"name": new_title}
    ).execute()

    new_form_id = copied["id"]

    print(f"✔ Duplicated form: {new_title}")
    print(f"  → New form ID: {new_form_id}")
    print(f"  → Edit URL: https://docs.google.com/forms/d/{new_form_id}/edit")

    return new_form_id
