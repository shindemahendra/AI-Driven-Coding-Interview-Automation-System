import os
import sys
import time
import signal
import subprocess
from pathlib import Path

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
    evaluate_l4_round,
)
from generate_candidate_test import run_candidate_test_generation

# ================================================================
# STREAMLIT CONFIG
# ================================================================
st.set_page_config(page_title="Interview Automation System", layout="wide")

# ================================================================
# CORPORATE UI THEME
# ================================================================
st.markdown("""
<style>
.stApp { background-color: #F8FAFC; }
h1 { color:#0F172A; font-weight:700; }
h2 { color:#1E293B; border-left:5px solid #2563EB; padding-left:8px; }
.block-container { padding-top: 1.2rem; }
[data-testid="stVerticalBlock"] > div {
    background:#FFF;
    border-radius:10px;
    padding:0.9rem;
    margin-bottom:0.7rem;
    box-shadow:0 4px 14px rgba(0,0,0,0.05);
}
.stButton > button {
    background:#2563EB;
    color:white;
    border-radius:8px;
    font-weight:600;
}
.stButton > button:hover { background:#1D4ED8; }
.instructions {
    background:#EFF6FF;
    border-left:4px solid #2563EB;
    padding:10px;
    border-radius:8px;
    font-size:0.85rem;
}
</style>
""", unsafe_allow_html=True)

# ================================================================
# TITLE + INSTRUCTIONS
# ================================================================
st.title("AI-Driven Coding Interview Automation System")

st.markdown("""
<div class="instructions">
<b>Usage Instructions</b><br>
• Enter candidate details and generate tests.<br>
• Start the timer when the candidate begins a round.<br>
• Stop the timer manually or let it auto-end.<br>
• Evaluate a round only after submission.
</div>
""", unsafe_allow_html=True)

# ================================================================
# SESSION STATE
# ================================================================
DEFAULT_STATE = {
    "latest_uid": None,
    "latest_candidate_name": None,
    "latest_candidate_email": None,
    "latest_difficulty": None,
    "latest_domain": None,
    "latest_json_path": None,
    "latest_form_ids": {},
    "l4_server_process": None,
    "timer_start_time": None,
    "active_round": None,
    "is_timer_running": False,
}

for k, v in DEFAULT_STATE.items():
    if k not in st.session_state:
        st.session_state[k] = v

TIMER_DURATION = 15 * 60

# ================================================================
# TIMER FUNCTIONS
# ================================================================
def start_timer(round_name):
    st.session_state.is_timer_running = True
    st.session_state.active_round = round_name
    st.session_state.timer_start_time = time.time()
    st.rerun()

def remaining_time():
    if not st.session_state.is_timer_running:
        return TIMER_DURATION
    elapsed = time.time() - st.session_state.timer_start_time
    return max(0, TIMER_DURATION - elapsed)

def stop_timer(manual=True):
    round_name = st.session_state.active_round
    st.session_state.is_timer_running = False
    st.session_state.active_round = None

    if manual:
        st.toast(f"{round_name} timer stopped manually")
    else:
        st.toast(f"{round_name} timer completed")

    st.rerun()

# ================================================================
# 1️⃣ CREATE INTERVIEW
# ================================================================
st.header("1. Create New Interview")

c1, c2, c3, c4 = st.columns(4)
candidate_name = c1.text_input("Candidate Name")
candidate_email = c2.text_input("Candidate Email")
difficulty = c3.selectbox("Difficulty", ["easy", "medium", "hard"], index=None)
domain = c4.selectbox("Domain", ["Python", "JavaScript"], index=None)

if st.button("Generate Test & Create Forms", key="create_interview"):
    if not all([candidate_name, candidate_email, difficulty, domain]):
        st.error("All fields are required")
    else:
        uid, json_path = run_candidate_test_generation(
            candidate_name.strip(),
            candidate_email.strip(),
            difficulty,
            domain,
        )

        st.session_state.latest_uid = uid
        st.session_state.latest_candidate_name = candidate_name
        st.session_state.latest_candidate_email = candidate_email
        st.session_state.latest_difficulty = difficulty
        st.session_state.latest_domain = domain
        st.session_state.latest_json_path = json_path

        forms = create_all_google_forms(json_path)

        # ---- Start L4 server (CROSS-PLATFORM SAFE) ----
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

        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0

        proc = subprocess.Popen(
            [sys.executable, PROJECT_ROOT / "coding_round_l4" / "exam_server.py", str(port)],
            cwd=str(PROJECT_ROOT / "coding_round_l4"),
            creationflags=creationflags,
        )

        time.sleep(1.2)

        st.session_state.l4_server_process = proc
        VM_IP = os.environ.get("VM_IP", "172.30.62.30")
        forms["L4"] = f"http://{VM_IP}:{port}"
        st.session_state.latest_form_ids = forms

        st.success("Interview created successfully")
        st.rerun()

# ================================================================
# INTERVIEW LINKS + TIMER
# ================================================================
if st.session_state.latest_form_ids:
    st.header("Interview Rounds & Timer")

    rounds = ["L1", "L2", "L3", "L4", "L5"]
    cols = st.columns(len(rounds))

    for i, lvl in enumerate(rounds):
        if lvl not in st.session_state.latest_form_ids:
            continue

        url = (
            st.session_state.latest_form_ids[lvl]
            if lvl == "L4"
            else f"https://docs.google.com/forms/d/{st.session_state.latest_form_ids[lvl]}/viewform"
        )

        with cols[i]:
            st.markdown(f"### {lvl}")
            st.markdown(f"[Open Test]({url})")

            if st.session_state.is_timer_running:
                if st.session_state.active_round == lvl:
                    st.button("⏳ Running", key=f"running_{lvl}", disabled=True)
                else:
                    st.button("Start Timer", key=f"disabled_{lvl}", disabled=True)
            else:
                if st.button(f"Start {lvl} Timer", key=f"start_{lvl}"):
                    start_timer(lvl)

    if st.session_state.is_timer_running:
        rem = remaining_time()
        mins, secs = divmod(int(rem), 60)

        st.info(f"⏱ {st.session_state.active_round} — {mins:02d}:{secs:02d}")

        if st.button("🛑 Stop Timer", key="stop_timer"):
            stop_timer(manual=True)

        if rem <= 0:
            stop_timer(manual=False)
        else:
            time.sleep(1)
            st.rerun()

# ================================================================
# 2️⃣ EVALUATE ROUND
# ================================================================
st.divider()
st.header("2. Evaluate Round")

json_path = st.text_input(
    "Candidate JSON Path",
    st.session_state.latest_json_path or "",
)

round_sel = st.selectbox("Select Round", ["L1", "L2", "L3", "L4", "L5"])
default_id = st.session_state.latest_form_ids.get(round_sel, "")
form_id = st.text_input("Form ID / L4 URL", default_id)

if st.button("Evaluate", key="evaluate_round"):
    if round_sel == "L4":
        info = {
            "uid": st.session_state.latest_uid,
            "name": st.session_state.latest_candidate_name,
            "email": st.session_state.latest_candidate_email,
        }
        res = evaluate_l4_round(
            str(PROJECT_ROOT / "coding_round_l4" / "l4_result.json"),
            info,
        )

        if res["status"] == "NO_SUBMISSION":
            st.warning("L4 not submitted yet")
        else:
            c1, c2, c3 = st.columns(3)
            c1.metric("Score (%)", res["score_percent"])
            c2.metric("Focus Lost", res["focus_lost"])
            c3.metric("Status", res["status"])

            if res.get("spreadsheet_id"):
                st.markdown(
                    f"[Open Result Sheet](https://docs.google.com/spreadsheets/d/{res['spreadsheet_id']})"
                )
    else:
        res = evaluate_round_core(form_id, json_path)
        if res["status"] == "NO_RESPONSES":
            st.warning("No responses yet")
        else:
            c1, c2 = st.columns(2)
            c1.metric("Score (%)", res["score_percent"])
            c2.metric("Status", res["status"])

            if res.get("spreadsheet_id"):
                st.markdown(
                    f"[Open Result Sheet](https://docs.google.com/spreadsheets/d/{res['spreadsheet_id']})"
                )
