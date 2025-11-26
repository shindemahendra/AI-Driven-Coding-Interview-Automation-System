from googleapiclient.discovery import build
from src.utils.sheet_reader_oauth import get_credentials

# -------------------------------------------------------
# GOOGLE FORMS API SERVICE
# -------------------------------------------------------
def get_forms_service():
    creds = get_credentials()
    service = build("forms", "v1", credentials=creds)
    return service

# -------------------------------------------------------
# GOOGLE DRIVE API SERVICE (for duplicating templates)
# -------------------------------------------------------
def get_drive_service():
    creds = get_credentials()
    service = build("drive", "v3", credentials=creds)
    return service
