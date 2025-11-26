import os
import pickle
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Define the scopes needed for Forms, Drive, and Sheets
SCOPES = [
    'https://www.googleapis.com/auth/forms',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets'
]


def get_google_service(api_name, api_version):
    """Initializes and authenticates a Google API service."""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Requires 'credentials.json' in the root folder
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build(api_name, api_version, credentials=creds)


try:
    # Initialize global API service objects
    DRIVE = get_google_service('drive', 'v3')
    FORMS = get_google_service('forms', 'v1')
    SHEETS = get_google_service('sheets', 'v4')
except Exception as e:
    # Use a more user-friendly error message for the Streamlit app
    print(
        f"FATAL AUTH ERROR: API services failed to initialize. Check credentials.json and internet connection. Error: {e}")
    DRIVE = FORMS = SHEETS = None


def initialize_sheet_headers(sheet_id):
    """Manually writes the required header columns to the Google Sheet."""
    if not SHEETS:
        raise Exception("Sheets API not initialized for header creation.")

    # These headers match the data the evaluation phase will eventually collect
    headers = [
        "Timestamp",
        "Candidate Full Name",
        "Candidate Email",
        "L4 Coding Submission",
        "L5 Soft Skill Response",
        "AI Coding Score (0-5)",
        "AI Soft Skill Score (0-5)",
        "AI Summary Feedback"
    ]

    body = {
        'values': [headers]
    }

    try:
        SHEETS.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range='Sheet1!A1',
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        print(f"Sheet {sheet_id} headers initialized successfully.")
    except HttpError as e:
        raise Exception(f"Sheets API Header Error: {e.content.decode()}")


def create_candidate_folder(candidate_name, parent_folder_id):
    """Creates a subfolder named after the candidate within the main parent folder."""
    if not DRIVE:
        raise Exception("Drive API not initialized for folder creation.")

    folder_name = f"Interview - {candidate_name}"
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_folder_id]
    }

    try:
        folder = DRIVE.files().create(body=file_metadata, fields='id').execute()
        print(f"Created candidate folder: {folder_name}")
        return folder.get('id')
    except HttpError as e:
        raise Exception(f"Drive API Folder Creation Error: {e.content.decode()}")


def create_interview_form(level_name, batch_name, candidate_folder_id):
    """Creates a Form, Sheet, moves them, and initializes sheet headers inside the candidate folder."""
    if not FORMS or not SHEETS or not DRIVE:
        raise Exception("API services are not initialized.")

    form_title = f"{level_name}_{batch_name}"

    try:
        # 1. Create a new Google Sheet (Response Target)
        spreadsheet_body = {'properties': {'title': f"Responses_{form_title}"}}
        sheet_resource = SHEETS.spreadsheets().create(
            body=spreadsheet_body,
            fields='spreadsheetId,spreadsheetUrl'
        ).execute()
        sheet_id = sheet_resource.get('spreadsheetId')
        sheet_url = sheet_resource.get('spreadsheetUrl')

        # 2. Create the new Google Form
        form_body = {'info': {'title': form_title, 'documentTitle': form_title}}
        form_resource = FORMS.forms().create(body=form_body).execute()

        form_id = form_resource.get('formId')
        form_url = form_resource.get('responderUri')

        # 3. Move Form and Sheet to the correct Drive folder
        # Files are created in the root folder, so we update the parent
        for file_id in [sheet_id, form_id]:
            # Use candidate_folder_id to move files to the newly created folder
            DRIVE.files().update(fileId=file_id, addParents=candidate_folder_id, removeParents='root').execute()

        # 4. Link the Form to the Spreadsheet
        # NOTE: Programmatic linking via batchUpdate consistently fails due to Google API errors
        # (e.g., "Unknown name"). This step is now skipped, and manual linking is required.
        print(f"*** WARNING: Please manually link Form {form_id} to Sheet {sheet_id} using the Form UI. ***")

        # 5. Initialize Sheet Headers Manually (Guarantees column order)
        initialize_sheet_headers(sheet_id)

        return form_id, form_url, sheet_id, sheet_url

    except HttpError as e:
        # Re-raise the error so the user sees the output for the failing step.
        raise Exception(f"Google API Error: {e.content.decode()}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {e}")


def populate_form_with_questions(form_id, questions_data):
    """
    STUB: Since programmatic question population consistently fails due to Forms API
    validation errors, this function is stubbed. Questions must be added manually
    to the form using the URL provided in the Streamlit output.
    """
    print(f"STUB: Skipping programmatic question population for Form {form_id}. Add questions manually.")
    # No action is performed to prevent the persistent HttpError 400.
    pass
