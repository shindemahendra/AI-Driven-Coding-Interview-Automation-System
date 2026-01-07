import json
import os

# -------------------------------------------------
# SESSION ID (MANDATORY, PORT-ISOLATED)
# -------------------------------------------------
SESSION_ID = os.environ.get("AZIRO_SESSION_ID")

if not SESSION_ID:
    raise RuntimeError(
        "AZIRO_SESSION_ID not set. "
        "Start Streamlit with AZIRO_SESSION_ID=<port_or_name>"
    )

STATE_DIR = "/opt/interview_app/state"
os.makedirs(STATE_DIR, exist_ok=True)

STATE_FILE = os.path.join(STATE_DIR, f"state_{SESSION_ID}.json")


def load_state():
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)