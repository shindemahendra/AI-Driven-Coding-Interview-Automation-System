from googleapiclient.discovery import build
from src.utils.sheet_reader_oauth import get_credentials
import os

DEPLOYMENT_ID = "AKfycbwbq-LrugsJpg6qkMgqYmX8gPpyhq2swf5sp-i6B9pMVZ7xIAelCvfXuTNs30ItH0Qlfw"


def call_apps_script(function_name, params):
    creds = get_credentials()
    service = build("script", "v1", credentials=creds)

    request = {
        "function": function_name,
        "parameters": [params],
        "devMode": False
    }

    response = service.scripts().run(
        scriptId=DEPLOYMENT_ID,
        body=request
    ).execute()

    if "error" in response:
        return response["error"]["details"][0].get("errorMessage", "Unknown error")

    return response.get("response", {}).get("result", "OK")
