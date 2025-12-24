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
# STATE MANAGER IMPORT
# ================================================================
from state_manager import load_state, save_state

# Load persistent state
_disk_state = load_state()

# Move to Streamlit state (sync)
if "ui" not in st.session_state:
    st.session_state.ui = _disk_state.copy()


def commit_state():
    """Sync st.session_state.ui → disk."""
    save_state(st.session_state.ui)


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
st.set_page_config(page_title="Aziro – Interview Automation", layout="wide")

# ================================================================
# BANNER
# ================================================================
BANNER_PATH = PROJECT_ROOT / "src" / "assets" / "aziro_banner.jpg"
if BANNER_PATH.exists():
    st.image(str(BANNER_PATH), use_container_width=True)

# ================================================================
# TITLE
# ================================================================
st.title("AI Interview Automation System")

# ================================================================
# SHORTCUTS
# ================================================================
ui = st.session_state.ui  # easier alias

# ================================================================
# CANDIDATES UI
# ================================================================
ui["apply_same"] = st.checkbox("Apply same difficulty & domain to all", value=ui["apply_same"])
ui["default_diff"] = st.selectbox("Default Difficulty", ["easy", "medium", "hard"], index=["easy", "medium", "hard"].index(ui["default_diff"]))
ui["default_domain"] = st.selectbox("Default Domain", ["Python", "JavaScript"], index=["Python", "JavaScript"].index(ui["default_domain"]))

st.divider()

if len(ui["candidates"]) < 10:
    if st.button("➕ Add Candidate"):
        ui["candidates"].append({
            "name": "",
            "email": "",
            "difficulty": ui["default_diff"],
            "domain": ui["default_domain"],
            "forms": None,
            "json_path": None,
            "cid": None,
        })
        commit_state()

for idx, cand in enumerate(ui["candidates"]):
    cols = st.columns([3, 3, 2, 2, 0.4])

    cand["name"] = cols[0].text_input("Name", cand["name"], key=f"name_{idx}")
    cand["email"] = cols[1].text_input("Email", cand["email"], key=f"email_{idx}")

    if ui["apply_same"]:
        cand["difficulty"] = ui["default_diff"]
        cand["domain"] = ui["default_domain"]
        cols[2].markdown(ui["default_diff"])
        cols[3].markdown(ui["default_domain"])
    else:
        cand["difficulty"] = cols[2].selectbox(
            "Difficulty", ["easy", "medium", "hard"], key=f"diff_{idx}", index=["easy", "medium", "hard"].index(cand["difficulty"])
        )
        cand["domain"] = cols[3].selectbox(
            "Domain", ["Python", "JavaScript"], key=f"dom_{idx}", index=["Python", "JavaScript"].index(cand["domain"])
        )

    if cols[4].button("✕", key=f"remove_{idx}"):
        ui["candidates"].pop(idx)
        commit_state()
        st.rerun()

commit_state()  # save intermediate edits

# ================================================================
# GENERATE TESTS
# ================================================================
if st.button("🚀 Generate Tests for All Candidates"):
    progress = st.progress(0)
    total = len(ui["candidates"])

    for i, cand in enumerate(ui["candidates"], start=1):
        uid, json_path = run_candidate_test_generation(
            cand["name"], cand["email"], cand["difficulty"], cand["domain"]
        )

        forms = create_all_google_forms(json_path)

        # Find free port
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

        progress.progress(i / total)

    commit_state()
    st.success("All candidate tests generated successfully")

# ================================================================
# TEST LINKS
# ================================================================
if ui["candidates"]:
    st.header("Test Links")

    for cand in ui["candidates"]:
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
# EVALUATION
# ================================================================
st.divider()
st.header("Evaluate Round")

candidate_labels = {f"{c['name']} ({c['email']})": c for c in ui["candidates"]}

ui["evaluation_selected_candidates"] = st.multiselect(
    "Select Candidate(s)",
    options=list(candidate_labels.keys()),
    default=ui["evaluation_selected_candidates"]
)

ui["evaluation_round"] = st.selectbox(
    "Select Round",
    ["L1", "L2", "L3", "L4", "L5"],
    index=["L1","L2","L3","L4","L5"].index(ui["evaluation_round"])
)

commit_state()

if st.button("Evaluate Selected"):
    results = []

    for label in ui["evaluation_selected_candidates"]:
        cand = candidate_labels[label]

        if ui["evaluation_round"] == "L4":
            res = evaluate_l4_round(
                str(PROJECT_ROOT / "coding_round_l4" / "l4_result.json"),
                {}
            )
        else:
            res = evaluate_round_core(cand["forms"][ui["evaluation_round"]], cand["json_path"])

        results.append({
            "Candidate": cand["name"],
            "Email": cand["email"],
            "Round": ui["evaluation_round"],
            "Score %": res.get("score_percent"),
            "Focus Lost": res.get("focus_lost", "-"),
            "Status": res["status"],
        })

    st.dataframe(pd.DataFrame(results), use_container_width=True)
    commit_state()
