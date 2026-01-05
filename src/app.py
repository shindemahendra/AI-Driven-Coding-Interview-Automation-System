import os
import sys
import time
import subprocess
from pathlib import Path
import socket

import streamlit as st
import pandas as pd

# ================================================================
# VM IP (DO NOT TOUCH – WORKING)
# ================================================================
def get_vm_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
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

if "l4_process" not in st.session_state:
    st.session_state.l4_process = None


def commit_state():
    def sanitize(obj):
        if isinstance(obj, dict):
            return {k: sanitize(v) for k, v in obj.items() if not hasattr(v, "pid")}
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
from src.utils.google_forms.save_results_to_sheet import save_round_result
from generate_candidate_test import run_candidate_test_generation_by_role

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

# ================================================================
# ROLE CONFIG
# ================================================================
ROLE_OPTIONS = {
    "Python Entry (0–2 yrs)": "python_entry",
    "Java Entry (0–2 yrs)": "java_entry",
    "JavaScript Entry (0–2 yrs)": "js_entry",
    "Python QA / System / Linux (4+ yrs)": "python_qa_linux",
    "Python QA (4+ yrs)": "python_qa",
    "Python Developer (4+ yrs)": "python_dev",
    "Python + AI/ML (4+ yrs)": "python_ai_ml",
    "Java + AWS (5+ yrs)": "java_aws",
    "Java QA (5+ yrs)": "java_qa",
}

DOMAIN_OPTIONS = ["None", "Storage", "Virtualization", "Networking"]

# ================================================================
# DEFAULTS
# ================================================================
ui.setdefault("candidates", [])
ui.setdefault("evaluation_cache", {})
ui.setdefault("evaluation_selected_candidates", [])
ui.setdefault("evaluation_round", "L1")
ui.setdefault("eval_all_rounds", False)

# ================================================================
# RESET
# ================================================================
_, reset_col = st.columns([8, 1])
with reset_col:
    if st.button("🔄 Reset"):
        if st.session_state.l4_process:
            try:
                st.session_state.l4_process.terminate()
            except Exception:
                pass

        st.session_state.ui = {
            "candidates": [],
            "evaluation_selected_candidates": [],
            "evaluation_round": "L1",
            "eval_all_rounds": False,
        }
        commit_state()
        st.rerun()

# ================================================================
# ADD CANDIDATE
# ================================================================
if len(ui["candidates"]) < 10:
    if st.button("➕ Add Candidate"):
        ui["candidates"].append({
            "name": "",
            "email": "",
            "role": list(ROLE_OPTIONS.values())[0],
            "domain": "None",
            "forms": None,
            "json_path": None,
        })
        commit_state()

# ================================================================
# CANDIDATE ROWS
# ================================================================
for idx, cand in enumerate(ui["candidates"]):
    cols = st.columns([3, 3, 3, 2, 0.4])

    cand["name"] = cols[0].text_input("Name", cand["name"], key=f"name_{idx}")
    cand["email"] = cols[1].text_input("Email", cand["email"], key=f"email_{idx}")

    role_label = cols[2].selectbox(
        "Role",
        options=list(ROLE_OPTIONS.keys()),
        index=list(ROLE_OPTIONS.values()).index(cand["role"]),
        key=f"role_{idx}",
    )
    cand["role"] = ROLE_OPTIONS[role_label]

    cand["domain"] = cols[3].selectbox(
        "Domain (optional)",
        DOMAIN_OPTIONS,
        index=DOMAIN_OPTIONS.index(cand["domain"]),
        key=f"domain_{idx}",
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

        domain_selected = cand["domain"] != "None"

        uid, json_path = run_candidate_test_generation_by_role(
            full_name=cand["name"],
            email=cand["email"],
            role_key=cand["role"],
            domain=None if not domain_selected else cand["domain"].lower(),
        )

        # ---- Create Google Forms from JSON ----
        raw_forms = create_all_google_forms(json_path)

        # ---- FIX: L5 / L6 MAPPING BASED ON DOMAIN ----
        forms = {}

        forms["L1"] = raw_forms.get("L1")
        forms["L2"] = raw_forms.get("L2")
        forms["L3"] = raw_forms.get("L3")

        # L4 is added later (coding)
        # L5/L6 logic:
        if domain_selected:
            # Domain → L5, Soft Skills → L6
            forms["L5"] = raw_forms.get("L5")   # domain
            forms["L6"] = raw_forms.get("L6")   # soft skills
        else:
            # No domain → Soft Skills stays at L5
            forms["L5"] = raw_forms.get("L5")

        # ---- START L4 CODING SERVER ----
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
        forms["L4"] = f"http://{get_vm_ip()}:{port}"

        cand["forms"] = forms
        cand["json_path"] = json_path

        progress.progress(i / total)

    commit_state()
    st.success("All candidate tests generated successfully")

# ================================================================
# TEST LINKS (UNCHANGED UI, SAFE)
# ================================================================
if ui["candidates"]:
    st.header("Test Links")
    for cand in ui["candidates"]:
        if not cand.get("forms"):
            continue

        st.subheader(cand["name"])
        cols = st.columns(6)

        for i, lvl in enumerate(["L1", "L2", "L3", "L4", "L5", "L6"]):
            link = cand["forms"].get(lvl)
            if not link:
                continue

            url = (
                link
                if lvl == "L4"
                else f"https://docs.google.com/forms/d/{link}/viewform"
            )
            cols[i].markdown(f"[Test ({lvl})]({url})")


# ================================================================
# EVALUATION
# ================================================================
st.divider()
st.header("Evaluation")

candidate_map = {
    f"{c['name']} ({c['email']})": c
    for c in ui["candidates"]
    if c.get("json_path")
}

ui["evaluation_selected_candidates"] = st.multiselect(
    "Select Candidate(s)",
    options=list(candidate_map.keys()),
    default=ui.get("evaluation_selected_candidates", []),
    key="eval_candidates"
)

ui["eval_all_rounds"] = st.checkbox(
    "Evaluate ALL rounds",
    value=ui.get("eval_all_rounds", False),
    key="eval_all"
)

ui["evaluation_round"] = st.selectbox(
    "Select Round",
    ["L1", "L2", "L3", "L4", "L5", "L6"],
    index=["L1", "L2", "L3", "L4", "L5", "L6"].index(
        ui.get("evaluation_round", "L1")
    ),
    disabled=ui["eval_all_rounds"],
    key="eval_round"
)

commit_state()


# ================================================================
# RUN EVALUATION (FIXED FEEDBACK + SAFE GUARDS)
# ================================================================
if st.button("Evaluate Selected", key="eval_btn"):

    if not ui["evaluation_selected_candidates"]:
        st.warning("⚠️ Please select at least one candidate.")
        st.stop()

    evaluated_any = False

    for label in ui["evaluation_selected_candidates"]:
        cand = candidate_map[label]

        if not cand.get("json_path"):
            continue

        uid = cand["json_path"].split("/")[-1].replace(".json", "")
        ui["evaluation_cache"].setdefault(uid, {})

        rounds = (
            ["L1", "L2", "L3", "L4", "L5", "L6"]
            if ui["eval_all_rounds"]
            else [ui["evaluation_round"]]
        )

        for rnd in rounds:

            # -------- L4 (CODING) --------
            if rnd == "L4":
                res = evaluate_l4_round(
                    str(PROJECT_ROOT / "coding_round_l4" / "l4_result.json"),
                    {
                        "uid": uid,
                        "name": cand["name"],
                        "email": cand["email"],
                    }
                )

            # -------- MCQ ROUNDS --------
            elif rnd in cand.get("forms", {}):
                res = evaluate_round_core(
                    cand["forms"][rnd],
                    cand["json_path"]
                )

            # -------- NOT ATTEMPTED --------
            else:
                res = {
                    "uid": uid,
                    "round_name": rnd,
                    "total_questions": 0,
                    "correct_count": 0,
                    "score_percent": 0.0,
                    "status": "NO_RESPONSE",
                    "details": [],
                }

            ui["evaluation_cache"][uid][rnd] = res
            evaluated_any = True

    commit_state()

    if evaluated_any:
        st.success("✅ Evaluation completed successfully.")
    else:
        st.warning("⚠️ No rounds were evaluated.")


# ================================================================
# CSV EXPORT + GOOGLE DRIVE UPLOAD
# ================================================================
import csv
from datetime import datetime
from src.utils.google_forms.form_api import get_drive_service

GOOGLE_DRIVE_FOLDER_ID = "1pcXw5Rn-2z3YBULkkbTmiPo91P9xxjRm"
LOCAL_TMP_DIR = "/opt/interview_app/tmp_results"
os.makedirs(LOCAL_TMP_DIR, exist_ok=True)


def generate_candidate_csv_and_upload(uid: str, cand: dict, results: dict):
    csv_path = f"{LOCAL_TMP_DIR}/{uid}_results.csv"
    ROUND_ORDER = ["L1", "L2", "L3", "L4", "L5", "L6"]

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "UID",
            "Candidate Name",
            "Email",
            "Round",
            "Total Questions",
            "Correct Answers",
            "Score %",
            "Status",
            "Last Updated",
        ])

        for rnd in ROUND_ORDER:
            res = results.get(rnd, {})
            writer.writerow([
                uid,
                cand["name"],
                cand["email"],
                rnd,
                res.get("total_questions", 0),
                res.get("correct_count", 0),
                res.get("score_percent", 0.0),
                res.get("status", "NO_RESPONSE"),
                datetime.now().isoformat(timespec="seconds"),
            ])

    drive = get_drive_service()
    file_name = f"{uid}_results.csv"

    query = (
        f"name='{file_name}' and "
        f"'{GOOGLE_DRIVE_FOLDER_ID}' in parents and trashed=false"
    )
    existing = drive.files().list(
        q=query, fields="files(id)"
    ).execute().get("files", [])

    for f in existing:
        drive.files().delete(fileId=f["id"]).execute()

    drive.files().create(
        body={
            "name": file_name,
            "parents": [GOOGLE_DRIVE_FOLDER_ID],
        },
        media_body=csv_path,
        fields="id",
    ).execute()


# ================================================================
# DISPLAY EVALUATION RESULTS (UI FEEDBACK)
# ================================================================
st.markdown("---")
st.header("Evaluation Results")

for label in ui["evaluation_selected_candidates"]:
    cand = candidate_map.get(label)
    if not cand or not cand.get("json_path"):
        continue

    uid = cand["json_path"].split("/")[-1].replace(".json", "")
    results = ui["evaluation_cache"].get(uid)

    if not results:
        continue

    name_col, btn_col = st.columns([6, 3])

    with name_col:
        st.subheader(f"{cand['name']} ({cand['email']})")

    with btn_col:
        if st.button(
            "📄 Save Results as CSV",
            key=f"csv_btn_{uid}"
        ):
            generate_candidate_csv_and_upload(
                uid=uid,
                cand=cand,
                results=results
            )
            st.success("✅ CSV generated & uploaded to Google Drive")

    # ---- Per-round details ----
    for rnd in ["L1", "L2", "L3", "L4", "L5", "L6"]:
        res = results.get(rnd)
        if not res:
            continue

        score = res.get("score_percent", 0.0)
        status = res.get("status", "NO_RESPONSE")

        with st.expander(f"{rnd} | {score}% | {status}"):
            st.json({
                "Total Questions": res.get("total_questions", 0),
                "Correct Answers": res.get("correct_count", 0),
                "Score %": score,
                "Status": status,
                "Details": res.get("details", []),
            })
