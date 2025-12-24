import json
from pathlib import Path

STATE_FILE = Path(__file__).resolve().parent.parent / "runtime_state" / "ui_state.json"

DEFAULT_STATE = {
    "candidates": [],
    "apply_same": False,
    "default_diff": "easy",
    "default_domain": "Python",
    "timer_running": False,
    "timer_start_ts": None,
    "evaluation_selected_candidates": [],
    "evaluation_round": "L1"
}


def load_state():
    """Load UI state from disk or return default state."""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_STATE.copy()


def save_state(state):
    """Persist UI state to disk."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
