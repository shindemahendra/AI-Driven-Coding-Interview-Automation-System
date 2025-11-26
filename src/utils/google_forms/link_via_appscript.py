import requests
import json
from src.utils.sheet_reader_oauth import get_credentials

# REPLACE WITH YOUR DEPLOYMENT ID
DEPLOYMENT_ID = "AKfycbz95aRwLw8OldRGhWniEs38iCKhlaJ7cUH-agunSyg1zXvbpELuWGAyJdLVfLtM0Io7uQ"

def call_appscript(form_id, sheet_id):
    creds = get_credentials()
    access_token = creds.token

    url = f"https://script.googleapis.com/v1/scripts/{DEPLOYMENT_ID}:run"

    payload = {
        "function": "linkFormToSheet",
        "parameters": [form_id, sheet_id]
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    res = requests.post(url, headers=headers, data=json.dumps(payload))

    print("STATUS:", res.status_code)
    print("RESPONSE:", res.text)
    return res
