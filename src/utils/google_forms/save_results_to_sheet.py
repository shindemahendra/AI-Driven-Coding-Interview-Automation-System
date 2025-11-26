# src/utils/google_forms/save_results_to_sheet.py

from datetime import datetime
from src.utils.google_forms.form_api import get_sheets_service, get_drive_service

# 👉 Your fixed folder ID where all result sheets will live
FOLDER_ID = "1pcXw5Rn-2z3YBULkkbTmiPo91P9xxjRm"


def _get_or_create_result_sheet(uid: str) -> str:
    """
    Find or create ONE results sheet per candidate.
    Sheet name: <uid>_results
    Returns: spreadsheetId
    """
    drive = get_drive_service()
    sheets = get_sheets_service()

    file_name = f"{uid}_results"

    # 1) Try to find existing spreadsheet in that folder
    query = (
        f"name = '{file_name}' and "
        f"'{FOLDER_ID}' in parents and "
        "mimeType = 'application/vnd.google-apps.spreadsheet' and "
        "trashed = false"
    )

    resp = drive.files().list(
        q=query,
        spaces="drive",
        fields="files(id, name)",
        pageSize=10,
    ).execute()

    files = resp.get("files", [])
    if files:
        return files[0]["id"]

    # 2) Create new spreadsheet
    body = {"properties": {"title": file_name}}
    sheet_resp = sheets.spreadsheets().create(body=body).execute()
    spreadsheet_id = sheet_resp["spreadsheetId"]

    # 3) Put it into the desired folder
    drive.files().update(
        fileId=spreadsheet_id,
        addParents=FOLDER_ID,
        fields="id, parents",
    ).execute()

    return spreadsheet_id


def save_round_result(
    uid: str,
    candidate_name: str,
    email: str,
    round_name: str,
    total_questions: int,
    correct_answers: int,
    score_percent: float,
    status: str,
) -> str:
    """
    Append one row for this round into the candidate's results sheet.

    Columns:
    UID | Candidate Name | Email | Round | Total Qs | Correct | Score % | Status | Timestamp
    """
    sheets = get_sheets_service()
    spreadsheet_id = _get_or_create_result_sheet(uid)

    sheet_name = "Sheet1"
    header_range = f"{sheet_name}!A1:I1"
    data_range = f"{sheet_name}!A1"

    # 1) Ensure header row exists
    header = [
        "UID",
        "Candidate Name",
        "Email",
        "Round",
        "Total Questions",
        "Correct Answers",
        "Score %",
        "Status",
        "Timestamp",
    ]

    header_resp = sheets.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=header_range,
    ).execute()

    if "values" not in header_resp:
        sheets.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=header_range,
            valueInputOption="RAW",
            body={"values": [header]},
        ).execute()

    # 2) Append this round result
    timestamp = datetime.now().isoformat(timespec="seconds")
    row = [
        uid,
        candidate_name,
        email,
        round_name,
        total_questions,
        correct_answers,
        score_percent,
        status,
        timestamp,
    ]

    sheets.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=data_range,
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": [row]},
    ).execute()

    return spreadsheet_id
