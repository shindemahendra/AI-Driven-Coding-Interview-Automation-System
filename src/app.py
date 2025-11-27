import streamlit as st
import pandas as pd
import re
import os
import sys
from pathlib import Path

# --- START FIX for ModuleNotFoundError: No module named 'src' ---
# This block ensures that the project root (the directory containing the 'src' folder)
# is added to the Python path, allowing imports like 'from src.utils...' to work.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))
# --- END FIX ---

# Import the core logic function from your new file
from src.utils.google_forms.create_all_forms import create_all_google_forms

# --- Configuration ---
# 1. HARDCODED MAIN INTERVIEW FOLDER ID (No longer strictly used by create_all_google_forms,
# but kept as a reminder of project setup if needed elsewhere.)
DEFAULT_FOLDER_ID = "10wVzl8MZKUX3ZzuqYphZ2MmmvOzT3vNL"

# Define the base directory where your pre-generated JSON tests are stored
# NOTE: This path is relative to the project root, which is now correctly in sys.path.
TEST_JSON_BASE_DIR = "question_bank/tests"


# Removed create_candidate_username as we now use an explicit UID


def get_json_path(candidate_uid: str, difficulty: str) -> str:
    """Constructs the expected path to the candidate's pre-generated test JSON using the UID."""
    # Example path: question_bank/tests/rbodicherla_easy.json
    return os.path.join(TEST_JSON_BASE_DIR, f"{candidate_uid.lower()}_{difficulty.lower()}.json")


def run_form_generation_workflow(candidate_name: str, candidate_email: str, candidate_uid: str, difficulty_level: str):
    """
    Orchestrates the workflow: finds the JSON path and calls the form creation logic.
    """

    json_path = get_json_path(candidate_uid, difficulty_level)

    st.info(f"Looking for pre-generated test JSON at path: `{json_path}`")

    # We must check existence relative to the project root, or wherever the script is run from.
    if not os.path.exists(json_path):
        st.error(f"❌ Error: Test JSON file not found for candidate '{candidate_uid}' at the expected path.")
        st.error(f"Please ensure the file `{json_path}` exists and contains the question data.")
        # Print the current working directory for debugging path issues
        st.info(f"Current working directory (Streamlit): {os.getcwd()}")
        return

    try:
        # Trigger the creation of all forms using the JSON file
        form_ids = create_all_google_forms(json_path)

        st.success("🎉 All Google Forms Created Successfully!")

        # Display results in a table
        master_tracker = []
        for level, form_id in form_ids.items():
            form_url = f"https://docs.google.com/forms/d/{form_id}/edit"
            master_tracker.append({
                'Candidate Name': candidate_name,
                'Candidate Email': candidate_email,
                'Level': level,
                'Form_URL': form_url
            })

        results_df = pd.DataFrame(master_tracker)
        st.dataframe(results_df, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Failed to create forms using JSON file: {e}")


# --- Streamlit UI ---

st.set_page_config(page_title="Interview Automation System", layout="wide")
st.title("🤖 AI-Driven Coding Interview Automation System")
st.divider()

# --- 1. Create New Interview Form ---
with st.container():
    st.header("1. Create New Interview Form")

    # Using 4 columns for a cleaner layout to fit all necessary inputs
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    # Input for Candidate Full Name (Display only)
    candidate_name = col1.text_input("Candidate Full Name", value="Ravi Bodicherla")

    # Input for Candidate Email
    candidate_email = col2.text_input("Candidate Email", value="rbodicherla@example.com")

    # Input for Candidate UID (Used for file lookup)
    candidate_uid = col3.text_input("Candidate UID (File Lookup Key)", value="rbodicherla")

    # Select box for Interview Level
    difficulty_options = ['easy', 'medium', 'hard']
    interview_level = col4.selectbox(
        "Interview Track (Selects the pre-generated JSON test)",
        options=difficulty_options,
        index=0,  # Default to easy, matching the provided JSON: rbodicherla_easy.json
    )

    st.markdown("---")

    st.subheader("Question Source: Pre-Generated JSON File")
    st.info("Forms will be created using a JSON file found at: `question_bank/tests/{candidate_uid}_{difficulty}.json`")

    if st.button("🚀 Create Interview Forms (All Levels)", type="primary"):
        # The button click triggers the new workflow, passing the UID
        run_form_generation_workflow(candidate_name, candidate_email, candidate_uid, interview_level)

st.divider()

# --- 2. Run Evaluation (Placeholder) ---
st.header("2. Run Evaluation & Generate Feedback")
st.warning("Phase 5/6 (Evaluation and Reporting) modules are not yet implemented in the provided code.")

if st.button("📈 Run Evaluation & Generate Reports", disabled=True):
    st.info("Evaluation process starting...")