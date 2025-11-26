from googleapiclient.discovery import build
from src.utils.sheet_reader_oauth import get_credentials

def create_response_sheet(title):
    creds = get_credentials()
    service = build("sheets", "v4", credentials=creds)

    sheet = service.spreadsheets().create(
        body={"properties": {"title": title}}
    ).execute()

    sheet_id = sheet["spreadsheetId"]
    print(f"✔ Created sheet: {title} ({sheet_id})")
    return sheet_id
