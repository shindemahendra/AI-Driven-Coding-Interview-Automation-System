import os
import sys
import time
import subprocess
from pathlib import Path

import streamlit as st
import pandas as pd
import socket

def get_vm_ip():
    """
    Reliable way to get VM IP (LAN/VPN safe).
    Does NOT use localhost.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't need to be reachable
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


# ================================================================
# PATH FIX
# ================================================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# ================================================================
# STATE MANAGER
# ================================================================
from state_manager import load_state, save_state

_disk_state = load_state()

if "ui" not in st.session_state:
    st.session_state.ui = _disk_state.copy()

# runtime-only
if "l4_process" not in st.session_state:
    st.session_state.l4_process = None


def commit_state():
    """Persist JSON-safe UI state only"""

    def sanitize(obj):
        if isinstance(obj, dict):
            return {
                k: sanitize(v)
                for k, v in obj.items()
                if not hasattr(v, "pid")
            }
        elif isinstance(obj, list):
            return [sanitize(v) for v in obj]
        return obj

    save_state(sanitize(st.session_state.ui))


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

st.title("AI Interview Automation System")
ui = st.session_state.ui

# ---------- Evaluation defaults (SAFE) ----------
ui.setdefault("evaluation_cache", {})
ui.setdefault("evaluation_selected_candidates", [])
ui.setdefault("evaluation_round", "L1")
ui.setdefault("eval_all_rounds", False)

# ================================================================
# RESET BUTTON
# ================================================================
_, reset_col = st.columns([8, 1])
with reset_col:
    if st.button("🔄 Reset"):
        if st.session_state.l4_process:
            try:
                st.session_state.l4_process.terminate()
            except Exception:
                pass
            st.session_state.l4_process = None

        st.session_state.ui = {
            "apply_same": False,
            "default_diff": "easy",
            "default_domain": "Python",
            "candidates": [],
            "evaluation_selected_candidates": [],
            "evaluation_round": "L1",
            "eval_all_rounds": False,
        }
        commit_state()
        st.rerun()

# ================================================================
# DEFAULTS
# ================================================================
ui.setdefault("apply_same", False)
ui.setdefault("default_diff", "easy")
ui.setdefault("default_domain", "Python")
ui.setdefault("candidates", [])
ui.setdefault("evaluation_selected_candidates", [])
ui.setdefault("evaluation_round", "L1")
ui.setdefault("eval_all_rounds", False)

# ================================================================
# CANDIDATE INPUT
# ================================================================
ui["apply_same"] = st.checkbox(
    "Apply same difficulty & domain to all",
    value=ui["apply_same"]
)

ui["default_diff"] = st.selectbox(
    "Default Difficulty",
    ["easy", "medium", "hard"],
    index=["easy", "medium", "hard"].index(ui["default_diff"])
)

ui["default_domain"] = st.selectbox(
    "Default Domain",
    ["Python", "JavaScript"],
    index=["Python", "JavaScript"].index(ui["default_domain"])
)

st.divider()

# ================================================================
# ADD CANDIDATE
# ================================================================
if len(ui["candidates"]) < 10:
    if st.button("➕ Add Candidate"):
        ui["candidates"].append({
            "name": "",
            "email": "",
            "difficulty": ui["default_diff"],
            "domain": ui["default_domain"],
            "forms": None,
            "json_path": None,
        })
        commit_state()

# ================================================================
# CANDIDATE ROWS
# ================================================================
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
            "Difficulty", ["easy", "medium", "hard"],
            index=["easy", "medium", "hard"].index(cand["difficulty"]),
            key=f"diff_{idx}"
        )
        cand["domain"] = cols[3].selectbox(
            "Domain", ["Python", "JavaScript"],
            index=["Python", "JavaScript"].index(cand["domain"]),
            key=f"dom_{idx}"
        )

    if cols[4].button("✕", key=f"remove_{idx}"):
        ui["candidates"].pop(idx)
        commit_state()
        st.rerun()

commit_state()

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

        proc = subprocess.Popen(
            [sys.executable, PROJECT_ROOT / "coding_round_l4" / "exam_server.py", str(port)],
            cwd=str(PROJECT_ROOT / "coding_round_l4"),
        )
        st.session_state.l4_process = proc

        time.sleep(1)
        vm_ip = get_vm_ip()
        forms["L4"] = f"http://{vm_ip}:{port}"

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
        if not cand.get("forms"):
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
st.header("Evaluation")

# -------- SAFETY DEFAULTS --------
ui.setdefault("evaluation_cache", {})
ui.setdefault("evaluation_selected_candidates", [])
ui.setdefault("evaluation_round", "L1")
ui.setdefault("eval_all_rounds", False)

candidate_map = {
    f"{c['name']} ({c['email']})": c for c in ui["candidates"]
}

ui["evaluation_selected_candidates"] = st.multiselect(
    "Select Candidate(s)",
    options=list(candidate_map.keys()),
    default=ui["evaluation_selected_candidates"]
)

ui["eval_all_rounds"] = st.checkbox(
    "Evaluate ALL rounds (L1–L5)",
    value=ui["eval_all_rounds"]
)

ui["evaluation_round"] = st.selectbox(
    "Select Round",
    ["L1", "L2", "L3", "L4", "L5"],
    index=["L1", "L2", "L3", "L4", "L5"].index(ui["evaluation_round"]),
    disabled=ui["eval_all_rounds"]
)

commit_state()

# ================================================================
# RUN EVALUATION (CORE FIX)
# ================================================================
if st.button("Evaluate Selected"):
    for label in ui["evaluation_selected_candidates"]:
        cand = candidate_map[label]
        uid = cand["json_path"].split("/")[-1].replace(".json", "")

        ui["evaluation_cache"].setdefault(uid, {})

        # ✅ Always consider all rounds if checkbox enabled
        rounds = (
            ["L1", "L2", "L3", "L4", "L5"]
            if ui["eval_all_rounds"]
            else [ui["evaluation_round"]]
        )

        for rnd in rounds:

            # ---------------- L4 ----------------
            if rnd == "L4":
                res = evaluate_l4_round(
                    str(PROJECT_ROOT / "coding_round_l4" / "l4_result.json"),
                    {
                        "uid": uid,
                        "name": cand["name"],
                        "email": cand["email"],
                    }
                )

            # ---------------- MCQ ROUNDS ----------------
            elif rnd in cand.get("forms", {}):
                res = evaluate_round_core(
                    cand["forms"][rnd],
                    cand["json_path"]
                )

            # ---------------- NOT ATTEMPTED ----------------
            else:
                res = {
                    "uid": uid,
                    "round_name": rnd,
                    "total_questions": 0,
                    "correct_count": 0,
                    "score_percent": 0.0,
                    "status": "NO_RESPONSE",
                    "details": [],
                    "spreadsheet_id": save_round_result(
                        uid=uid,
                        candidate_name=cand["name"],
                        email=cand["email"],
                        round_name=rnd,
                        total_questions=0,
                        correct_answers=0,
                        score_percent=0.0,
                        status="NO_RESPONSE",
                    )
                }

            # Cache result (UI only)
            ui["evaluation_cache"][uid][rnd] = res

    commit_state()

from src.utils.google_forms.save_results_to_sheet import save_round_result


def generate_candidate_sheet_from_ui(uid: str, cand: dict, results: dict):
    """
    Generate / overwrite Google Sheet using UI evaluation_cache.
    EXACTLY 5 rows (L1–L5).
    This function is called ONLY when HR clicks the button.
    """

    for rnd in ["L1", "L2", "L3", "L4", "L5"]:
        res = results.get(rnd)

        # ---------------- NOT ATTEMPTED ----------------
        if not res:
            save_round_result(
                uid=uid,
                candidate_name=cand["name"],
                email=cand["email"],
                round_name=rnd,
                total_questions=0,
                correct_answers=0,
                score_percent=0.0,
                status="NO_RESPONSE",
            )
            continue

        # ---------------- ATTEMPTED ----------------
        save_round_result(
            uid=uid,
            candidate_name=cand["name"],
            email=cand["email"],
            round_name=rnd,
            total_questions=res.get("total_questions", 0),
            correct_answers=res.get("correct_count", 0),
            score_percent=res.get("score_percent", 0.0),
            status=res.get("status", "UNKNOWN"),
        )


# ================================================================
# DISPLAY RESULTS (UNCHANGED STRUCTURE)
# ================================================================
st.markdown("---")

for label in ui["evaluation_selected_candidates"]:
    cand = candidate_map[label]
    uid = cand["json_path"].split("/")[-1].replace(".json", "")

    results = ui["evaluation_cache"].get(uid)
    if not results:
        continue

    name_col, btn_col = st.columns([6, 2])

    with name_col:
        st.markdown(f"### {cand['name']} ({cand['email']})")

    with btn_col:
        if st.button(
                "💾 Save & Generate Sheet",
                key=f"save_sheet_{uid}",
        ):
            generate_candidate_sheet_from_ui(
                uid=uid,
                cand=cand,
                results=ui["evaluation_cache"].get(uid, {})
            )
            st.success("Result sheet generated successfully")

    # Single sheet link per candidate
    sheet_id = next(
        (r.get("spreadsheet_id") for r in results.values() if r.get("spreadsheet_id")),
        None
    )
    if sheet_id:
        st.markdown(
            f"[📄 Open Result Sheet](https://docs.google.com/spreadsheets/d/{sheet_id})"
        )

    for rnd in ["L1", "L2", "L3", "L4", "L5"]:
        res = results.get(rnd)
        if not res:
            continue

        with st.expander(f"{rnd} | {res['score_percent']}% | {res['status']}"):
            st.json(res.get("details", []))


