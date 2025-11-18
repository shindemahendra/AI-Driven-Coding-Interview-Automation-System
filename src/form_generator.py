import os
import pickle
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
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build(api_name, api_version, credentials=creds)


try:
    DRIVE = get_google_service('drive', 'v3')
    FORMS = get_google_service('forms', 'v1')
    SHEETS = get_google_service('sheets', 'v4')
except Exception as e:
    print(f"FATAL AUTH ERROR: {e}")
    DRIVE = FORMS = SHEETS = None


def create_interview_form(level_name, batch_name, parent_folder_id):
    """Creates a Form, Sheet, links them, and moves them to the Drive folder."""
    if not FORMS or not SHEETS or not DRIVE:
        raise Exception("API services are not initialized.")

    form_title = f"{level_name}_{batch_name}"

    try:
        # 1. Create a new Google Sheet (Response Target)
        sheet_resource = SHEETS.spreadsheets().create(
            body={'properties': {'title': f"Responses_{form_title}"}},
            fields='spreadsheetId,spreadsheetUrl'
        ).execute()
        sheet_id = sheet_resource.get('spreadsheetId')
        sheet_url = sheet_resource.get('spreadsheetUrl')

        # 2. Create the new Google Form
        form_resource = FORMS.forms().create(
            body={'info': {'title': form_title, 'documentTitle': form_title}}
        ).execute()

        form_id = form_resource.get('formId')
        form_url = form_resource.get('responderUri')

        # 3. Move Form and Sheet to the correct Drive folder
        for file_id in [sheet_id, form_id]:
            DRIVE.files().update(fileId=file_id, addParents=parent_folder_id, removeParents='root').execute()

        # 4. Link the Form to the Sheet
        link_request = {"requests": [{"updateFormSettings": {
            "settings": {"responseDestinations": [{"type": "SHEET", "sheetId": sheet_id}]},
            "updateMask": "responseDestinations"}}]}
        FORMS.forms().batchUpdate(formId=form_id, body=link_request).execute()

        return form_id, form_url, sheet_id, sheet_url

    except HttpError as e:
        raise Exception(f"Google API Error: {e.content.decode()}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {e}")


def populate_form_with_questions(form_id, questions_data):
    """Takes generated questions and pushes them to the form."""
    requests = []
    # (Simplified: This loop needs to build requests for TEXT, CHOICE, etc.)
    for question in questions_data:
        q_title = question.get('title', 'Untitled Question')
        q_type = question.get('type')

        # Example for TEXT question (L4 Coding, L5 Soft Skills)
        if q_type == 'TEXT':
            requests.append({
                "createItem": {
                    "item": {"title": q_title, "questionItem": {"textQuestion": {"paragraph": True}}},
                    "location": {"index": -1}  # Add at the end
                }
            })
        # Note: Full CHOICE question logic requires building the multipleChoiceQuestion object

    if requests:
        FORMS.forms().batchUpdate(formId=form_id, body={"requests": requests}).execute()
        print(f"Form {form_id} populated with {len(requests)} questions.")