from src.utils.google_forms.google_service_utils import get_forms_service


def disable_google_form(form_id: str, round_name: str) -> bool:
    """
    Closes the Google Form by setting 'acceptingResponses' to False.
    This function implements the actual API call using batchUpdate.

    Args:
        form_id: The ID of the Google Form to close.
        round_name: The round name (L1, L2, etc.) for logging purposes.

    Returns:
        True if the form was successfully disabled, False otherwise.
    """
    forms_service = get_forms_service()

    if forms_service is None:
        print(f"[ERROR] Could not initialize Google Forms Service. Failed to disable form {form_id}.")
        return False

    print(f"[INFO] Attempting to disable Google Form for Round {round_name} (ID: {form_id})...")

    # The request payload for batchUpdate to disable responses
    request_body = {
        'requests': [
            {
                'updateFormInfo': {
                    'info': {
                        # We only need to specify the field we want to update
                        'acceptingResponses': False
                    },
                    # This tells the API which field in the FormInfo object to update
                    'updateMask': 'acceptingResponses'
                }
            }
        ]
    }

    try:
        # Call the Forms API batchUpdate method
        # The result object confirms the update was accepted by the API
        forms_service.forms().batchUpdate(
            formId=form_id,
            body=request_body
        ).execute()

        print(f"[SUCCESS] Google Form for Round {round_name} (ID: {form_id}) successfully disabled.")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to disable Google Form {form_id} for Round {round_name}. API Error: {e}")
        return False

# You can now update the Streamlit app's stub in app.py to import and use this function:
# from src.utils.google_forms.manage_form_status import disable_google_form