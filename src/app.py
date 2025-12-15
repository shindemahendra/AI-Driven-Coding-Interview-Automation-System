import os
import sys
import time
import signal
import subprocess
from pathlib import Path

import pandas as pd
import streamlit as st

# ================================================================
# PATH FIX
# ================================================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# ================================================================
# IMPORTS
# ================================================================
from src.utils.google_forms.manage_form_status import disable_google_form
from src.utils.google_forms.create_all_forms import create_all_google_forms
from src.utils.google_forms.evaluate_round import (
    evaluate_round_core,
    check_if_response_exists,
    evaluate_l4_round
)

try:
    from generate_candidate_test import run_candidate_test_generation
except Exception:
    st.error("generate_candidate_test.py missing in project root")

# ================================================================
# STREAMLIT CONFIG
# ================================================================
st.set_page_config(page_title="Interview Automation System", layout="wide")
st.title("AI-Driven Coding Interview Automation System")
st.divider()

# ================================================================
# SESSION STATE INITIALIZATION (IMPORTANT FIX)
# ================================================================
SESSION_KEYS = {
    "latest_uid": None,
    "latest_candidate_name": None,
    "latest_candidate_email": None,
    "latest_difficulty": None,
    "latest_domain": None,
    "latest_json_path": None,
    "latest_form_ids": {},          # ✅ FIX
    "l4_server_process": None,
    "latest_l4_url": None,
    "timer_start_time": None,
    "active_round": None,
    "is_timer_running": False,
}

for key, default in SESSION_KEYS.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ================================================================
# CONSTANTS
# ================================================================
TEST_JSON_BASE_DIR = "question_bank/tests"
TIMER_DURATION_SECONDS = 15 * 60

# ================================================================
# TIMER HELPERS
# ================================================================
def start_timer(round_name):
    st.session_state.is_timer_running = True
    st.session_state.timer_start_time = time.time()
    st.session_state.active_round = round_name
    st.rerun()

def get_remaining_time():
    if not st.session_state.is_timer_running:
        return TIMER_DURATION_SECONDS
    elapsed = time.time() - st.session_state.timer_start_time
    return max(0, TIMER_DURATION_SECONDS - elapsed)

def stop_timer_and_disable_form(round_name, form_id, reason):
    st.session_state.is_timer_running = False
    st.session_state.active_round = None
    if form_id:
        disable_google_form(form_id, round_name)
    st.toast(f"{round_name} ended: {reason}")
    st.rerun()

# ================================================================
# L4 SERVER MANAGEMENT
# ================================================================
def kill_l4_server():
    proc = st.session_state.l4_server_process
    if proc and proc.poll() is None:
        try:
            os.kill(proc.pid, signal.SIGTERM)
        except Exception:
            pass
    st.session_state.l4_server_process = None
    st.session_state.latest_l4_url = None

def start_l4_server():
    kill_l4_server()

    import socket
    port = 5001
    while True:
        try:
            s = socket.socket()
            s.bind(("127.0.0.1", port))
            s.close()
            break
        except OSError:
            port += 1

    exam_server = PROJECT_ROOT / "coding_round_l4" / "exam_server.py"

    proc = subprocess.Popen(
        [sys.executable, exam_server, str(port)],
        cwd=str(PROJECT_ROOT / "coding_round_l4"),  # 🔥 FIX
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
    )

    # ✅ give Flask time to boot
    time.sleep(1.5)

    st.session_state.l4_server_process = proc
    st.session_state.latest_l4_url = f"http://localhost:{port}"
    return st.session_state.latest_l4_url


# ================================================================
# 1️⃣ CREATE INTERVIEW
# ================================================================
st.header("1. Create New Interview")

col1, col2, col3, col4 = st.columns(4)
candidate_name = col1.text_input("Candidate Name")
candidate_email = col2.text_input("Candidate Email")
difficulty = col3.selectbox("Difficulty", ["easy", "medium", "hard"], index=None)
domain = col4.selectbox("Domain", ["Python", "JavaScript"], index=None)

if st.button("Generate Test & Create Forms"):
    if not all([candidate_name, candidate_email, difficulty, domain]):
        st.error("All fields are required")
    else:
        uid, json_path = run_candidate_test_generation(
            candidate_name.strip(),
            candidate_email.strip(),
            difficulty,
            domain
        )

        st.session_state.latest_uid = uid
        st.session_state.latest_candidate_name = candidate_name
        st.session_state.latest_candidate_email = candidate_email
        st.session_state.latest_difficulty = difficulty
        st.session_state.latest_domain = domain
        st.session_state.latest_json_path = json_path

        # Create Google Forms
        form_ids = create_all_google_forms(json_path)

        # Start L4 server
        l4_url = start_l4_server()
        form_ids["L4"] = l4_url

        st.session_state.latest_form_ids = form_ids
        st.success("Interview created successfully")
        st.rerun()

# ================================================================
# LINKS + TIMER
# ================================================================
if st.session_state.latest_form_ids:
    st.subheader("Interview Links")

    for level in ["L1", "L2", "L3", "L4", "L5"]:
        if level not in st.session_state.latest_form_ids:
            continue

        link = st.session_state.latest_form_ids[level]
        if level == "L4":
            url = link
        else:
            url = f"https://docs.google.com/forms/d/{link}/viewform"

        st.markdown(f"{level}: [Open]({url})")

# ================================================================
# 2️⃣ EVALUATE ROUND
# ================================================================
st.divider()
st.header("2. Evaluate Round")

json_path = st.text_input(
    "Candidate JSON Path",
    st.session_state.latest_json_path or ""
)

selected_round = st.selectbox("Select Round", ["L1", "L2", "L3", "L4", "L5"])

default_form = st.session_state.latest_form_ids.get(selected_round, "")
form_id = st.text_input("Form ID / L4 URL", default_form)

if st.button("Evaluate"):
    if selected_round == "L4":
        result = evaluate_l4_round("coding_round_l4/l4_result.json")

        if result["status"] == "NO_SUBMISSION":
            st.warning("L4 not submitted yet")
        else:
            st.metric("Score (%)", result["score_percent"])
            st.metric("Focus Lost", result["focus_lost"])
            st.metric("Status", result["status"])
    else:
        result = evaluate_round_core(form_id, json_path)

        if result["status"] == "NO_RESPONSES":
            st.warning("No responses yet")
        else:
            st.metric("Score (%)", result["score_percent"])
            st.metric("Status", result["status"])
