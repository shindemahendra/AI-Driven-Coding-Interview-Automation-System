# src/utils/google_forms/form_linker.py
from googleapiclient.errors import HttpError


# from src.utils.google_forms.service import get_forms_service # Import your Forms service

def link_form_to_sheet(form_id, spreadsheet_id, forms_service):
    """
    Uses Forms API batchUpdate to link a form to a specific spreadsheet ID.
    """
    update_request = {
        "requests": [
            {
                "updateFormProperties": {
                    "properties": {
                        "collectResponses": True,  # Ensure response collection is enabled
                        "destinationId": spreadsheet_id,
                        "destinationType": "SPREADSHEET"
                    },
                    "updateMask": "destinationId,destinationType,collectResponses"
                }
            }
        ]
    }

    try:
        forms_service.forms().batchUpdate(
            formId=form_id,
            body=update_request
        ).execute()

        print(f"  ✅ Form linked to Sheet ID: {spreadsheet_id}")
        return True

    except HttpError as error:
        print(f"  🚨 An error occurred while linking form: {error}")
        return False