import os
import sys
from pathlib import Path
import time

import pandas as pd
import streamlit as st

# =================================================================
# 1. PATH FIX: Ensure project root is on sys.path for internal imports
# This must happen immediately before any imports from 'src.*'
# =================================================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))
# =================================================================


# =================================================================
# 2. APPLICATION IMPORTS (Now that the path is fixed)
# =================================================================
# Import the function needed for the timer stop logic
from src.utils.google_forms.manage_form_status import disable_google_form

try:
    # Assuming generate_candidate_test.py is in the project root (not src/)
    # NOTE: The signature for this function should now accept 'domain' as a fourth argument.
    from generate_candidate_test import run_candidate_test_generation
except ImportError:
    st.error(
        "Could not import 'run_candidate_test_generation'. Please ensure 'generate_candidate_test.py' is in the project root."
    )


    # Updated placeholder to include 'domain'
    def run_candidate_test_generation(name, email, difficulty, domain):
        raise NotImplementedError("run_candidate_test_generation is not available.")

# NOTE: These utility modules must be available
from src.utils.google_forms.create_all_forms import create_all_google_forms
from src.utils.google_forms.evaluate_round import evaluate_round_core
# IMPORTANT: This function must be implemented in src/utils/google_forms/evaluate_round.py
from src.utils.google_forms.evaluate_round import check_if_response_exists

# =================================================================


TEST_JSON_BASE_DIR = "question_bank/tests"

# --- CONFIGURATION ---
TIMER_DURATION_SECONDS = 15 * 60  # 15 minutes


def get_json_path_from_uid(uid: str, difficulty: str) -> str:
    """Helper: construct full JSON path."""
    return os.path.join(TEST_JSON_BASE_DIR, f"{uid.lower()}_{difficulty.lower()}.json")


# ------------------ STREAMLIT APP CONFIG ------------------

st.set_page_config(page_title="Interview Automation System", layout="wide")
st.title("🤖 AI-Driven Coding Interview Automation System")
st.divider()

# Initialize session_state
for key in [
    "latest_uid",
    "latest_candidate_name",
    "latest_candidate_email",
    "latest_difficulty",
    "latest_domain",  # <-- NEW: Store the domain
    "latest_json_path",
    "latest_form_ids",
    # Timer-related state
    "timer_start_time",
    "active_round",
    "is_timer_running",
]:
    if key not in st.session_state:
        # Initialize default values
        if key == "is_timer_running":
            st.session_state[key] = False
        elif key == "active_round":
            st.session_state[key] = None
        else:
            st.session_state[key] = None


# --- Timer Logic Functions ---

def start_timer(round_name: str):
    """Starts the timer for a specific round."""
    # Reset any previous timer state when a new one starts
    st.session_state.is_timer_running = True
    st.session_state.timer_start_time = time.time()
    st.session_state.active_round = round_name
    st.rerun()


def get_remaining_time_seconds():
    """Calculates the remaining time in seconds."""
    if st.session_state.is_timer_running and st.session_state.timer_start_time is not None:
        elapsed_time = time.time() - st.session_state.timer_start_time
        remaining = TIMER_DURATION_SECONDS - elapsed_time
        return max(0, remaining)
    return TIMER_DURATION_SECONDS


def format_time(seconds):
    """Formats seconds into mm:ss string."""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}m {seconds:02d}s"


def stop_timer_and_disable_form(ended_round: str, form_id_to_disable: str, reason: str):
    """Centralized logic to stop timer, close form, and update UI."""
    # Stop the timer state
    st.session_state.is_timer_running = False
    st.session_state.active_round = None

    # Attempt to disable the form via the API call
    if form_id_to_disable:
        try:
            # 3️⃣ Disable the form using the API
            disable_google_form(form_id_to_disable, ended_round)
            st.info(
                f"🚨 Round **{ended_round}** ended ({reason}). The Google Form has been **CLOSED**.")
        except Exception as api_e:
            st.error(
                f"🚨 Round **{ended_round}** ended, but failed to close the form via API: {api_e}")
    else:
        st.error(f"🚨 Round **{ended_round}** ended, but the form ID was not found.")

    st.toast(f"Round {ended_round} finished!")
    st.rerun()


# ======================
# 1. CREATE INTERVIEW
# ======================

with st.container():
    st.header("1. Create New Interview Forms")

    # Change to 4 columns to include Domain
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    candidate_name = col1.text_input("Candidate Full Name", value="")
    candidate_email = col2.text_input("Candidate Email", value="")

    difficulty_options = ["easy", "medium", "hard"]
    difficulty = col3.selectbox(
        "Difficulty Level",
        options=difficulty_options,
        index=None,
        placeholder="Select difficulty",
    )

    # NEW: Domain selection
    domain_options = ["Python", "JavaScript"]
    domain = col4.selectbox(
        "Coding Domain",
        options=domain_options,
        index=None,
        placeholder="Select domain",
    )

    st.markdown("---")
    st.subheader("Generation Flow")
    st.markdown(
        """
        1. Generate a **candidate test JSON** (L1–L5) using master banks.  
        2. Use that JSON to **create 5 Google Forms** (L1, L2, L3, L5, optional L4 coding).  
        3. Below you will get **Google Form links** and the **Timed Test Controls**.
        """
    )

    if st.button("🚀 Generate Test & Create Google Forms", type="primary"):
        if not candidate_name.strip() or not candidate_email.strip():
            st.error("Please enter both candidate name and email.")
        elif difficulty is None:
            st.error("Please select a difficulty level.")
        elif domain is None:  # NEW check
            st.error("Please select a coding domain.")
        else:
            try:
                # 1️⃣ Generate candidate test JSON
                # NOTE: Passing the new 'domain' argument
                uid, json_path = run_candidate_test_generation(
                    candidate_name.strip(),
                    candidate_email.strip(),
                    difficulty.strip().lower(),
                    domain.strip()  # <-- NEW ARGUMENT
                )

                st.session_state["latest_uid"] = uid
                st.session_state["latest_candidate_name"] = candidate_name.strip()
                st.session_state["latest_candidate_email"] = candidate_email.strip()
                st.session_state["latest_difficulty"] = difficulty.strip().lower()
                st.session_state["latest_domain"] = domain.strip()  # <-- NEW: Store domain
                st.session_state["latest_json_path"] = json_path

                st.success(
                    f"✅ Candidate test JSON generated for **{candidate_name}** "
                    f"(UID: `{uid}`, Domain: `{domain}`, difficulty: `{difficulty}`)\n\n"  # Updated message
                    f"📁 JSON Path: `{json_path}`"
                )

                # 2️⃣ Create forms
                form_ids = create_all_google_forms(json_path)
                st.session_state["latest_form_ids"] = form_ids

                st.success("🎉 All Google Forms created successfully!")
                st.rerun()

            except Exception as e:
                st.error(f"❌ Unexpected error during generation: {e}")

    # ============= DISPLAY LINKS & TIMER BUTTONS BLOCK =============
    if st.session_state.get("latest_form_ids"):
        st.subheader("Generated Interview Links")
        st.markdown("Click any link below to open the form.")

        form_ids = st.session_state["latest_form_ids"]
        uid = st.session_state.get("latest_uid", "unknown_uid")

        target_order = ["L1", "L2", "L3", "L4", "L5"]
        sorted_levels = [level for level in target_order if level in form_ids]

        # Use st.expander for a cleaner look if many forms are generated
        with st.expander("Forms"):
            # Create a header row (Round, Google Form Link)
            header_cols = st.columns([1, 2])
            header_cols[0].markdown("**Round**")
            header_cols[1].markdown("**Google Form Link**")
            st.markdown("---")

            for level in sorted_levels:
                form_id = form_ids[level]
                google_link = f"https://docs.google.com/forms/d/{form_id}/viewform"

                # Display Links (Only Round and Google Form Link)
                cols = st.columns([1, 2])
                cols[0].markdown(f"**{level}**")
                cols[1].markdown(f'🔗 <a href="{google_link}" target="_blank">Open Form</a>', unsafe_allow_html=True)
                # Removed the timed link column (cols[2])

        st.markdown("---")

        # --- Timer Control Panel ---
        st.subheader("⏱ Candidate Test Timer (15 Minutes)")

        # Timer control logic uses a single row of columns for compactness
        timer_cols = st.columns(len(sorted_levels) + 1)

        # Display the Start buttons
        for i, level in enumerate(sorted_levels):
            button_key = f"start_timer_{level}"
            is_active_round = st.session_state.active_round == level
            is_timer_running = st.session_state.is_timer_running

            button_text = f"▶️ Start {level} Timer"

            if is_timer_running and is_active_round:
                # If this round is active, disable the button and show running status
                timer_cols[i].button(
                    f"Running ({level})",
                    key=button_key,
                    disabled=True,
                    type="secondary"
                )
            elif is_timer_running and not is_active_round:
                # If another round is active, disable this button
                timer_cols[i].button(
                    f"Start {level} Timer",
                    key=button_key,
                    disabled=True,
                    help=f"Timer is running for {st.session_state.active_round}"
                )
            else:
                # If no timer is running, allow starting this round
                if timer_cols[i].button(button_text, key=button_key, type="primary"):
                    start_timer(level)

        # Display Stop Button in the last column
        with timer_cols[-1]:
            if st.session_state.is_timer_running:
                if st.button("⏹ Stop Timer", key="stop_timer_btn", type="secondary"):
                    # Manual stop just clears state; it does NOT close the form.
                    # The user can still choose to close it manually or run evaluation.
                    st.session_state.is_timer_running = False
                    st.session_state.active_round = None
                    st.toast("Timer manually stopped.")
                    st.rerun()
            else:
                st.button("⏹ Stop Timer", key="stop_timer_btn_disabled", disabled=True)

        # --- Timer Status Display ---
        if st.session_state.is_timer_running:
            remaining_seconds = get_remaining_time_seconds()

            ended_round = st.session_state.active_round
            form_ids = st.session_state.get("latest_form_ids", {})
            form_id_to_disable = form_ids.get(ended_round)

            # 1. Check for Early Submission
            if form_id_to_disable:
                try:
                    # Check if a response has been submitted since the timer started
                    if check_if_response_exists(form_id_to_disable):
                        stop_timer_and_disable_form(
                            ended_round, form_id_to_disable, "Candidate submitted form early"
                        )

                except Exception as e:
                    # Log warning but continue timer if API check fails
                    st.warning(f"Failed to check for form response (continuing timer): {e}")

            # 2. Check for Time Expiration (Only if not stopped early)
            if remaining_seconds <= 0:
                stop_timer_and_disable_form(
                    ended_round, form_id_to_disable, "Time's up"
                )
            else:
                # Timer continues running
                time_remaining_str = format_time(remaining_seconds)

                # Calculate progress (value between 0.0 and 1.0)
                progress_value = 1.0 - (remaining_seconds / TIMER_DURATION_SECONDS)
                progress_percent = progress_value  # st.progress uses 0.0 to 1.0

                st.subheader(f"Round {st.session_state.active_round} Remaining:")
                st.markdown(
                    f'<div style="font-size: 2em; font-weight: bold; color: #ff4b4b;">{time_remaining_str}</div>',
                    unsafe_allow_html=True)

                st.progress(progress_percent)

                # Rerun every second to update the time display
                time.sleep(1)
                st.rerun()

        st.markdown("---")

st.divider()

# ======================
# 2. EVALUATE A ROUND
# ======================

st.header("2. Evaluate a Round & Save Result")

st.markdown(
    """
Select a **round**, choose the Google Form, and the system will:

- Fetch latest submission
- Compare with candidate JSON  
- Compute **score, percentage, pass/fail** - Save into your Google Sheets results folder  
"""
)

if st.session_state["latest_uid"]:
    st.info(
        f"Latest candidate: **{st.session_state['latest_candidate_name']}** "
        f"(UID: `{st.session_state['latest_uid']}`, Domain: `{st.session_state.get('latest_domain', 'N/A')}`, difficulty: `{st.session_state['latest_difficulty']}`)"
    )
else:
    st.warning("No candidate context found. You can still evaluate manually.")

default_json_path = st.session_state.get("latest_json_path") or ""
json_path_eval = st.text_input(
    "Candidate Test JSON Path",
    value=default_json_path,
    placeholder="question_bank/tests/<uid>_<difficulty>.json",
)

round_options_eval = ["L1", "L2", "L3", "L4", "L5"]
selected_round = st.selectbox("Select Round to Evaluate", options=round_options_eval)

default_form_id = ""
if st.session_state.get("latest_form_ids"):
    default_form_id = st.session_state["latest_form_ids"].get(selected_round, "")

form_id_input = st.text_input(
    "Google Form ID for this round",
    value=default_form_id,
    placeholder="Paste Form ID here",
)

if st.button("✅ Evaluate Selected Round", type="secondary"):
    form_id_clean = form_id_input.strip()
    json_path_clean = json_path_eval.strip()

    if not form_id_clean:
        st.error("Please provide a valid Google Form ID.")
    elif not json_path_clean or not os.path.exists(json_path_clean):
        st.error(f"JSON not found at: `{json_path_clean}`")
    else:
        try:
            result = evaluate_round_core(form_id_clean, json_path_clean)

            if result["status"] == "NO_RESPONSES":
                st.warning("⚠ No responses submitted yet.")
            elif result["status"] == "NO_EVALUATABLE_QUESTIONS":
                st.warning("⚠ No evaluatable questions found (maybe titles didn't match).")
            else:
                st.subheader("Round Evaluation Result")

                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Total Questions", result["total_questions"])
                col_b.metric("Correct Answers", result["correct_count"])
                col_c.metric("Score (%)", f"{result['score_percent']}%")

                if result["status"] == "PASS":
                    st.success(f"✅ PASSED ({result['score_percent']}%)")
                else:
                    st.error(f"❌ FAILED ({result['score_percent']}%)")

                if result["spreadsheet_id"]:
                    sheet_url = f"https://docs.google.com/spreadsheets/d/{result['spreadsheet_id']}"
                    st.markdown(f"📊 Stored in Google Sheet: [Open Sheet]({sheet_url})")

                if result["details"]:
                    with st.expander("Question-wise Details"):
                        rows = []
                        for d in result["details"]:
                            rows.append(
                                {
                                    "Level": d["level"],
                                    "Question": d["title"],
                                    "User Answer": d["user_answer"],
                                    "Correct Answer": d["correct_answer"],
                                    "Correct?": "✅" if d["is_correct"] else "❌",
                                }
                            )
                        st.dataframe(pd.DataFrame(rows), use_container_width=True)

        except Exception as e:
            st.error(f"❌ Failed to evaluate: {e}")