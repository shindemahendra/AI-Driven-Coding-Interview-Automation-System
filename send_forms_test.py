import json
import requests
import os

WEB_APP_URL = "https://script.google.com/a/macros/aziro.com/s/AKfycbxLWj-1mfAlErAxXcIgIKL1xw-s5jblD_8sPN9zzhf-6MfWFO8pUGidNjw_iYqnPw5f/exec"
file_name = input("Enter candidate test JSON file (ex: rbodicherla_easy.json): ").strip()
file_path = os.path.join("question_bank", "tests", file_name)

if not os.path.exists(file_path):
    print(f"❌ File not found: {file_path}")
    exit()

with open(file_path, "r", encoding="utf-8") as f:
    payload = json.load(f)

res = requests.post(WEB_APP_URL, json=payload)

print("Status Code:", res.status_code)
print("Response:", res.text)
