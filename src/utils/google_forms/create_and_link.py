from src.utils.google_forms.create_sheet import create_response_sheet
from src.utils.google_forms.link_via_appscript import call_appscript

def auto_create_sheet_and_link(form_id, uid, level):
    # Create the response Google Sheet
    sheet_title = f"{uid}_{level}_responses"
    sheet_id = create_response_sheet(sheet_title)

    print(f"✔ Created response sheet: {sheet_title} ({sheet_id})")

    # Link form → sheet using Apps Script
    call_appscript(form_id, sheet_id)

    print(f"✔ Linked form {level} → sheet {sheet_title}")
    return sheet_id
