from googleapiclient.discovery import build
from src.utils.sheet_reader_oauth import get_credentials

def get_sheets_service():
    creds = get_credentials()
    return build("sheets", "v4", credentials=creds)
