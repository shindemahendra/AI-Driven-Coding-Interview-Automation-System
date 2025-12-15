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

    body = {"properties": {"title": file_name}}
    sheet_resp = sheets.spreadsheets().create(body=body).execute()
    spreadsheet_id = sheet_resp["spreadsheetId"]

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
    focus_violations: int = 0,  # ✅ NEW (backward compatible)
) -> str:
    """
    Append one row for this round into the candidate's results sheet.

    Columns:
    UID | Candidate Name | Email | Round | Total Qs | Correct | Score % | Focus Violations | Status | Timestamp
    """
    sheets = get_sheets_service()
    spreadsheet_id = _get_or_create_result_sheet(uid)

    sheet_name = "Sheet1"
    header_range = f"{sheet_name}!A1:J1"
    data_range = f"{sheet_name}!A1"

    header = [
        "UID",
        "Candidate Name",
        "Email",
        "Round",
        "Total Questions",
        "Correct Answers",
        "Score %",
        "Focus Violations",   # ✅ NEW
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

    timestamp = datetime.now().isoformat(timespec="seconds")
    row = [
        uid,
        candidate_name,
        email,
        round_name,
        total_questions,
        correct_answers,
        score_percent,
        focus_violations,     # ✅ NEW
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
