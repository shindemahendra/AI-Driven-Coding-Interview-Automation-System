import os
import sys
import time
import subprocess
from pathlib import Path

import streamlit as st
import pandas as pd

# ================================================================
# PATH FIX
# ================================================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# ================================================================
# IMPORTS (UNCHANGED)
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
st.set_page_config(page_title="Aziro – Interview Automation", layout="wide")

# ================================================================
# UI THEME (UNCHANGED)
# ================================================================
st.markdown("""
<style>
.stApp { background-color:#F8FAFC; }

h1 { color:#0F172A; font-weight:700; margin-bottom:0.4rem; }
h2 {
    color:#1E293B;
    border-left:4px solid #2563EB;
    padding-left:8px;
    margin-top:1rem;
}

.instructions {
    background:#EFF6FF;
    border-left:4px solid #2563EB;
    padding:10px;
    border-radius:8px;
    font-size:0.85rem;
    margin-bottom:0.8rem;
}

input {
    background:#F9FAFB !important;
    border-radius:6px !important;
}

.stButton>button {
    background:#2563EB;
    color:white;
    border-radius:6px;
    font-weight:600;
}
.stButton>button:hover { background:#1D4ED8; }

.remove-btn button {
    background:transparent !important;
    color:#64748B !important;
    padding:0.15rem 0.4rem !important;
    font-size:14px !important;
    border:none !important;
}
</style>
""", unsafe_allow_html=True)

# ================================================================
# TITLE + INSTRUCTIONS
# ================================================================
st.title("Aziro – AI-Driven Interview Automation")

st.markdown("""
<div class="instructions">
<b>HR Instructions</b><br>
• Add up to 10 candidates and generate tests.<br>
• Share test links with candidates and start the common timer.<br>
• Timer applies to all candidates & rounds.<br>
• Evaluate rounds only after submission.
</div>
""", unsafe_allow_html=True)

# ================================================================
# SESSION STATE
# ================================================================
if "candidates" not in st.session_state:
    st.session_state.candidates = []

if "timer_running" not in st.session_state:
    st.session_state.timer_running = False

if "timer_start_ts" not in st.session_state:
    st.session_state.timer_start_ts = None

# ================================================================
# TIMER HELPERS (UNCHANGED)
# ================================================================
TIMER_DURATION = 15 * 60

def start_timer():
    st.session_state.timer_running = True
    st.session_state.timer_start_ts = time.time()

def stop_timer():
    st.session_state.timer_running = False
    st.session_state.timer_start_ts = None

def remaining_time():
    if not st.session_state.timer_running:
        return TIMER_DURATION
    elapsed = time.time() - st.session_state.timer_start_ts
    return max(0, TIMER_DURATION - elapsed)

# ================================================================
# 1️⃣ CREATE TESTS FOR CANDIDATES + TIMER (UNCHANGED)
# ================================================================
header_col, timer_col = st.columns([4, 1])

with header_col:
    st.header("1. Create Tests for Candidates")

with timer_col:
    st.markdown("**⏱ Timer**")

    if not st.session_state.timer_running:
        if st.button("▶ Start", key="timer_start"):
            start_timer()
            st.rerun()
    else:
        if st.button("🛑 Stop", key="timer_stop"):
            stop_timer()
            st.rerun()

    if st.session_state.timer_running:
        rem = remaining_time()
        mins, secs = divmod(int(rem), 60)
        st.markdown(f"**{mins:02d}:{secs:02d}**")

        if rem <= 0:
            stop_timer()
            st.toast("⏱ Timer completed")
            st.rerun()
        else:
            time.sleep(1)
            st.rerun()

# ================================================================
# MULTI-CANDIDATE INPUT (UNCHANGED)
# ================================================================
apply_same = st.checkbox("Apply same difficulty & domain to all")

default_diff = st.selectbox("Default Difficulty", ["easy", "medium", "hard"])
default_domain = st.selectbox("Default Domain", ["Python", "JavaScript"])

st.divider()

if len(st.session_state.candidates) < 10:
    if st.button("➕ Add Candidate"):
        st.session_state.candidates.append({
            "name": "",
            "email": "",
            "difficulty": default_diff,
            "domain": default_domain,
            "forms": None,
        })

for idx, cand in enumerate(st.session_state.candidates):
    cols = st.columns([3, 3, 2, 2, 0.6])

    cand["name"] = cols[0].text_input("Name", cand["name"], key=f"name_{idx}")
    cand["email"] = cols[1].text_input("Email", cand["email"], key=f"email_{idx}")

    if apply_same:
        cand["difficulty"] = default_diff
        cand["domain"] = default_domain
        cols[2].markdown(default_diff)
        cols[3].markdown(default_domain)
    else:
        cand["difficulty"] = cols[2].selectbox(
            "Difficulty", ["easy", "medium", "hard"],
            index=["easy", "medium", "hard"].index(cand["difficulty"]),
            key=f"diff_{idx}"
        )
        cand["domain"] = cols[3].selectbox(
            "Domain", ["Python", "JavaScript"],
            index=["Python", "JavaScript"].index(cand["domain"]),
            key=f"dom_{idx}"
        )

    with cols[4]:
        if st.button("✕", key=f"remove_{idx}"):
            st.session_state.candidates.pop(idx)
            st.rerun()

# ================================================================
# GENERATE TESTS (UNCHANGED)
# ================================================================
if st.button("🚀 Generate Tests for All Candidates"):
    progress = st.progress(0)
    total = len(st.session_state.candidates)

    for i, cand in enumerate(st.session_state.candidates):
        uid, json_path = run_candidate_test_generation(
            cand["name"].strip(),
            cand["email"].strip(),
            cand["difficulty"],
            cand["domain"],
        )

        forms = create_all_google_forms(json_path)

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

        subprocess.Popen(
            [sys.executable, PROJECT_ROOT / "coding_round_l4" / "exam_server.py", str(port)],
            cwd=str(PROJECT_ROOT / "coding_round_l4"),
        )
        time.sleep(1)

        VM_IP = os.environ.get("VM_IP", "localhost")
        forms["L4"] = f"http://{VM_IP}:{port}"

        cand["forms"] = forms
        cand["json_path"] = json_path
        progress.progress((i + 1) / total)

    st.success("All candidate tests generated successfully")

# ================================================================
# TEST LINKS (UNCHANGED)
# ================================================================
if st.session_state.candidates:
    st.header("2. Test Links")

    for cand in st.session_state.candidates:
        if not cand["forms"]:
            continue

        st.subheader(cand["name"])
        cols = st.columns(5)
        for i, lvl in enumerate(["L1", "L2", "L3", "L4", "L5"]):
            link = cand["forms"].get(lvl)
            if not link:
                continue

            url = link if lvl == "L4" else f"https://docs.google.com/forms/d/{link}/viewform"
            cols[i].markdown(f"[Test ({lvl})]({url})")

# ================================================================
# 3️⃣ EVALUATE ROUND (ENHANCED – SAFE)
# ================================================================
st.divider()
st.header("3. Evaluate Round")

candidate_labels = {
    f"{c['name']} ({c['email']})": c for c in st.session_state.candidates
}

selected_candidates = st.multiselect(
    "Select Candidate(s)",
    options=list(candidate_labels.keys())
)

round_sel = st.selectbox("Select Round", ["L1", "L2", "L3", "L4", "L5"])

if st.button("Evaluate Selected"):
    if not selected_candidates:
        st.warning("Please select at least one candidate")
    else:
        results = []
        progress = st.progress(0)
        total = len(selected_candidates)

        for i, label in enumerate(selected_candidates, start=1):
            cand = candidate_labels[label]

            if round_sel == "L4":
                res = evaluate_l4_round(
                    str(PROJECT_ROOT / "coding_round_l4" / "l4_result.json"),
                    {
                        "uid": cand.get("uid"),
                        "name": cand["name"],
                        "email": cand["email"],
                    }
                )
            else:
                form_id = cand["forms"].get(round_sel)
                res = evaluate_round_core(form_id, cand["json_path"])

            results.append({
                "Candidate": cand["name"],
                "Email": cand["email"],
                "Round": round_sel,
                "Score %": res.get("score_percent"),
                "Focus Lost": res.get("focus_lost", "-"),
                "Status": res["status"],
                "Sheet": res.get("spreadsheet_id", "-"),
            })

            progress.progress(i / total)

        progress.empty()
        st.success("Evaluation completed")

        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True)
