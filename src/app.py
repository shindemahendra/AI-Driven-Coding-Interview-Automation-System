import os
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# --- Ensure project root is on sys.path so "src. ..." imports work ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# --- Imports from your project ---
from generate_candidate_test import run_candidate_test_generation
from src.utils.google_forms.create_all_forms import create_all_google_forms
from src.utils.google_forms.evaluate_round import evaluate_round_core

# Where candidate test JSON files are stored
TEST_JSON_BASE_DIR = "question_bank/tests"


# Helper: construct full JSON path (for info / manual override)
def get_json_path_from_uid(uid: str, difficulty: str) -> str:
    return os.path.join(TEST_JSON_BASE_DIR, f"{uid.lower()}_{difficulty.lower()}.json")


# ------------------ STREAMLIT APP CONFIG ------------------

st.set_page_config(page_title="Interview Automation System", layout="wide")
st.title("🤖 AI-Driven Coding Interview Automation System")
st.divider()

# Initialize session_state slots (for later evaluation) if not set
for key in [
    "latest_uid",
    "latest_candidate_name",
    "latest_candidate_email",
    "latest_difficulty",
    "latest_json_path",
    "latest_form_ids",
]:
    if key not in st.session_state:
        st.session_state[key] = None

# ======================
# 1. CREATE INTERVIEW
# ======================

with st.container():
    st.header("1. Create New Interview Forms")

    col1, col2, col3 = st.columns([1, 1, 1])

    candidate_name = col1.text_input("Candidate Full Name", value="Ravi Kumar Bodicherla")
    candidate_email = col2.text_input("Candidate Email", value="rbodicherla@example.com")

    difficulty_options = ["easy", "medium", "hard"]
    difficulty = col3.selectbox(
        "Difficulty Level",
        options=difficulty_options,
        index=0,
    )

    st.markdown("---")
    st.subheader("Generation Flow")
    st.markdown(
        """
        1. Generate a **candidate test JSON** (L1–L5) using master banks.  
        2. Use that JSON to **create 5 Google Forms** (L1, L2, L3, L5, and optional L4 coding).  
        3. Show the **form links** below (click to open, copy for HR to share).
        """
    )

    if st.button("🚀 Generate Test & Create Google Forms", type="primary"):
        if not candidate_name.strip() or not candidate_email.strip():
            st.error("Please enter both candidate name and email.")
        else:
            try:
                # 1️⃣ Generate candidate test JSON (all rounds for selected difficulty)
                uid, json_path = run_candidate_test_generation(
                    candidate_name.strip(),
                    candidate_email.strip(),
                    difficulty.strip().lower(),
                )

                st.session_state["latest_uid"] = uid
                st.session_state["latest_candidate_name"] = candidate_name.strip()
                st.session_state["latest_candidate_email"] = candidate_email.strip()
                st.session_state["latest_difficulty"] = difficulty.strip().lower()
                st.session_state["latest_json_path"] = json_path

                st.success(
                    f"✅ Candidate test JSON generated for **{candidate_name}** "
                    f"(UID: `{uid}`, difficulty: `{difficulty}`)\n\n"
                    f"📁 JSON Path: `{json_path}`"
                )

                # 2️⃣ Create all Google Forms from this JSON
                form_ids = create_all_google_forms(json_path)
                # create_all_google_forms is expected to return: { "L1": formId, "L2": ..., ... }
                st.session_state["latest_form_ids"] = form_ids

                st.success("🎉 All Google Forms created successfully!")

                # 3️⃣ Show forms in a small summary table
                st.subheader("Generated Google Forms")

                table_rows = []
                for level, form_id in form_ids.items():
                    form_url = f"https://docs.google.com/forms/d/{form_id}/edit"
                    table_rows.append(
                        {
                            "Round": level,
                            "Form URL": form_url,
                            "Open": f"[Open {level} Form]({form_url})",
                        }
                    )

                if table_rows:
                    df = pd.DataFrame(table_rows)
                    # Show as Markdown so links are clickable
                    st.markdown("**Forms Overview**")
                    st.markdown(df[["Round", "Open"]].to_markdown(index=False), unsafe_allow_html=True)

                    st.markdown("**Copy Form Links**")
                    st.info(
                        "Use the boxes below to copy each form URL easily and share with the candidate."
                    )
                    for row in table_rows:
                        level = row["Round"]
                        url = row["Form URL"]
                        st.text_input(
                            label=f"{level} Form Link",
                            value=url,
                            key=f"copy_{level}",
                        )

            except FileNotFoundError as fe:
                st.error(f"❌ {fe}")
            except Exception as e:
                st.error(f"❌ Unexpected error during form generation: {e}")

st.divider()

# ======================
# 2. EVALUATE A ROUND
# ======================

st.header("2. Evaluate a Round & Save Result")

st.markdown(
    """
Select a **round**, pick the associated Google Form, and the system will:

- Fetch the **latest submission** from that Form  
- Compare each MCQ answer with the **candidate JSON**  
- Compute **score, percentage, pass/fail**  
- Store the result in a per-candidate **Google Sheet** inside your fixed results folder  
"""
)

# Help text: last candidate context
if st.session_state["latest_uid"]:
    st.info(
        f"Latest candidate context: **{st.session_state['latest_candidate_name']}** "
        f"(UID: `{st.session_state['latest_uid']}`, difficulty: `{st.session_state['latest_difficulty']}`)"
    )
else:
    st.warning(
        "No candidate context detected in this session. You can still manually provide JSON path and Form ID below."
    )

# JSON path (pre-filled with latest if available)
default_json_path = st.session_state.get("latest_json_path") or ""
json_path_eval = st.text_input(
    "Candidate Test JSON Path",
    value=default_json_path,
    placeholder="e.g., question_bank/tests/<uid>_<difficulty>.json",
)

# Round selection
round_options = ["L1", "L2", "L3", "L5"]
selected_round = st.selectbox("Select Round to Evaluate", options=round_options, index=0)

# Auto-fetch formId for that round if we have it
default_form_id = ""
if st.session_state.get("latest_form_ids"):
    default_form_id = st.session_state["latest_form_ids"].get(selected_round, "")

form_id_input = st.text_input(
    "Google Form ID for this round",
    value=default_form_id,
    placeholder="Paste Form ID here if not auto-filled",
)

if st.button("✅ Evaluate Selected Round", type="secondary"):
    form_id_clean = form_id_input.strip()
    json_path_clean = json_path_eval.strip()

    if not form_id_clean:
        st.error("Please provide a valid Google Form ID.")
    elif not json_path_clean or not os.path.exists(json_path_clean):
        st.error(f"JSON file not found at: `{json_path_clean}`")
    else:
        try:
            result = evaluate_round_core(form_id_clean, json_path_clean)

            status = result["status"]
            if status == "NO_RESPONSES":
                st.warning("⚠ No responses found for this form yet.")
            elif status == "NO_EVALUATABLE_QUESTIONS":
                st.warning("⚠ No evaluatable questions found (maybe titles didn't match).")
            else:
                # Show summary
                st.subheader("Round Evaluation Result")

                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Total Questions", result["total_questions"])
                with col_b:
                    st.metric("Correct Answers", result["correct_count"])
                with col_c:
                    st.metric(
                        "Score (%)",
                        f"{result['score_percent']}%",
                        help="Pass threshold: 75%",
                    )

                passed = result["status"] == "PASS"
                st.success_msg = (
                    f"✅ **PASSED** ({result['score_percent']}%)"
                    if passed
                    else f"❌ **FAILED** ({result['score_percent']}%)"
                )

                if passed:
                    st.success(st.success_msg)
                else:
                    st.error(st.success_msg)

                st.write(
                    f"**Detected Round:** `{result['round_name']}`  |  "
                    f"**Candidate:** {result['candidate_name']}  |  "
                    f"**Email:** {result['email']}"
                )

                # Link to Google Sheet
                if result["spreadsheet_id"]:
                    sheet_url = f"https://docs.google.com/spreadsheets/d/{result['spreadsheet_id']}"
                    st.markdown(
                        f"📊 Results stored in Google Sheet: [Open Sheet]({sheet_url})"
                    )

                # Detailed per-question breakdown
                if result["details"]:
                    with st.expander("Show Question-wise Details"):
                        detail_rows = []
                        for d in result["details"]:
                            detail_rows.append(
                                {
                                    "Level": d["level"],
                                    "Question": d["title"],
                                    "User Answer": d["user_answer"],
                                    "Correct Answer": d["correct_answer"],
                                    "Is Correct?": "✅" if d["is_correct"] else "❌",
                                }
                            )
                        detail_df = pd.DataFrame(detail_rows)
                        st.dataframe(detail_df, use_container_width=True)
            # end if status
        except Exception as e:
            st.error(f"❌ Failed to evaluate round: {e}")
