import os
import sys
import time
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
# UI THEME
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
</style>
""", unsafe_allow_html=True)

# ================================================================
# TITLE
# ================================================================
st.title("AI-Driven Coding Interview Automation System")

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
}

for k, v in DEFAULT_STATE.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ================================================================
# CREATE INTERVIEW
# ================================================================
st.header("Create Interview")

c1, c2, c3, c4 = st.columns(4)
candidate_name = c1.text_input("Candidate Name")
candidate_email = c2.text_input("Candidate Email")
difficulty = c3.selectbox("Difficulty", ["easy", "medium", "hard"], index=None)
domain = c4.selectbox("Domain", ["Python", "JavaScript"], index=None)

if st.button("Generate Test & Create Forms"):
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

        # ---------- START L4 SERVER ----------
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

        cmd = [
            sys.executable,
            str(PROJECT_ROOT / "coding_round_l4" / "exam_server.py"),
            str(port),
        ]

        if os.name == "nt":  # Windows
            proc = subprocess.Popen(
                cmd,
                cwd=str(PROJECT_ROOT / "coding_round_l4"),
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            )
        else:  # Linux / Mac
            proc = subprocess.Popen(
                cmd,
                cwd=str(PROJECT_ROOT / "coding_round_l4"),
                start_new_session=True,
            )

        time.sleep(1.2)

        st.session_state.l4_server_process = proc
        forms["L4"] = f"http://localhost:{port}"
        st.session_state.latest_form_ids = forms

        st.success("Interview created successfully")

# ================================================================
# INTERVIEW LINKS
# ================================================================
if st.session_state.latest_form_ids:
    st.header("Interview Rounds")

    for lvl, fid in st.session_state.latest_form_ids.items():
        if lvl == "L4":
            url = fid
        else:
            url = f"https://docs.google.com/forms/d/{fid}/viewform"
        st.markdown(f"**{lvl}** → [Open Test]({url})")

# ================================================================
# EVALUATION
# ================================================================
st.divider()
st.header("Evaluate Round")

round_sel = st.selectbox("Select Round", ["L1", "L2", "L3", "L4", "L5"])
form_id = st.text_input("Form ID / L4 URL")

if st.button("Evaluate"):
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
        st.json(res)
    else:
        res = evaluate_round_core(form_id, st.session_state.latest_json_path)
        st.json(res)
