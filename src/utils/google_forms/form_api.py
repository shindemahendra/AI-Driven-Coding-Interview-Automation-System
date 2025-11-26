# src/utils/google_forms/form_api.py

from googleapiclient.discovery import build
from src.utils.sheet_reader_oauth import get_credentials


def get_forms_service():
    """Return an authenticated Google Forms API service."""
    creds = get_credentials()
    return build("forms", "v1", credentials=creds)


def get_sheets_service():
    """Return an authenticated Google Sheets API service."""
    creds = get_credentials()
    return build("sheets", "v4", credentials=creds)


def get_drive_service():
    """Return an authenticated Google Drive API service."""
    creds = get_credentials()
    return build("drive", "v3", credentials=creds)
