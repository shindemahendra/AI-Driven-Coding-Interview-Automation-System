import streamlit as st
import pandas as pd
import json
import os
from form_generator import create_interview_form, populate_form_with_questions, create_candidate_folder

# Note: The 'ai_generator' module is assumed to exist for the AI Generation mode
# from ai_generator import generate_questions_for_level

# --- Configuration ---
# 1. HARDCODED MAIN INTERVIEW FOLDER ID
# IMPORTANT: REPLACE "YOUR_HARDCODED_MAIN_INTERVIEW_FOLDER_ID" with your actual Google Drive Folder ID.
DEFAULT_FOLDER_ID = "10wVzl8MZKUX3ZzuqYphZ2MmmvOzT3vNL"

LEVELS_CONFIG = {
    'L1': 'Logical Puzzles',
    'L2': 'MCQs & Syntax',
    'L3': 'System Design Fundamentals',
    'L4': 'Coding Problems',
    'L5': 'Soft-skill Situational Questions'
}


def generate_questions_for_level(level, q_type):
    """
    STUB FUNCTION: Replace with actual Gemini API call logic in ai_generator.py.
    For now, this returns a placeholder list if needed, or an error if the real
    module isn't available.
    """
    st.warning(f"Stub used: AI generation for {level} is not fully implemented.")
    # Return placeholder for L4/L5 if needed for testing, otherwise an empty list
    if level == 'L4':
        return [{'question': 'STUB: Write a sorting algorithm (L4)', 'options': []}]
    elif level == 'L5':
        return [{'question': 'STUB: Describe a conflict (L5)', 'options': []}]
    else:
        # Placeholder for L1-L3
        return [{'question': f'STUB: What is 1+1? ({level})', 'options': ['2', '3']}]


def run_form_generation(batch_name, candidate_name, main_folder_id):
    """Executes the full Form Creation and Question Population workflow, always using AI Generation (stubbed)."""
    st.info(f"Initiating new batch: **{batch_name}** for **{candidate_name}** using **AI Generation**...")
    master_tracker = []

    if main_folder_id == "YOUR_HARDCODED_MAIN_INTERVIEW_FOLDER_ID":
        st.error(
            "🛑 Please hardcode the 'DEFAULT_FOLDER_ID' variable in src/app.py to a real Google Drive Folder ID before running.")
        return pd.DataFrame()

    try:
        # P1: Create the Candidate Folder first
        candidate_folder_id = create_candidate_folder(candidate_name, main_folder_id)
        st.success(f"✅ Created candidate folder: Interview - {candidate_name}")
    except Exception as e:
        st.error(f"❌ Failed to create candidate folder for {candidate_name}: {e}")
        return pd.DataFrame()  # Stop if folder creation fails

    for level, q_type in LEVELS_CONFIG.items():
        st.markdown(f"**-> Creating {level} ({q_type}) in candidate folder...**")

        # --- Question Source Logic: Always use AI Generation (Stubbed) ---
        questions_data = generate_questions_for_level(level, q_type)
        # -----------------------------

        try:
            # P2: Create Form, Sheet, Move, and Initialize Headers
            # Pass the candidate_folder_id instead of the main_folder_id
            form_id, form_url, sheet_id, sheet_url = create_interview_form(level, batch_name, candidate_folder_id)

            # P3: Populate Questions (Uses stub implementation in form_generator.py)
            if questions_data:
                populate_form_with_questions(form_id, questions_data)

            st.success(f"✅ {level} Form Created: [View Form]({form_url}) | [View Sheet]({sheet_url})")

            master_tracker.append({'Level': level, 'Form_URL': form_url, 'Sheet_URL': sheet_url})

        except Exception as e:
            st.error(f"❌ Failed to create {level}: {e}")

    if master_tracker:
        results_df = pd.DataFrame(master_tracker)
        st.subheader("🎉 Batch Creation Complete!")
        st.dataframe(results_df)
        return results_df
    return pd.DataFrame()


# --- Streamlit UI ---

st.set_page_config(page_title="AI Interview Automation System", layout="wide")
st.title("🤖 AI-Driven Coding Interview Automation System")
st.divider()

# --- 1. Create New Interview Batch ---
with st.container():
    st.header("1. Create New Interview Batch")

    col1, col2 = st.columns([1, 1])

    # Input for Candidate Full Name
    candidate_name = col1.text_input("Candidate Full Name", value="Jane Doe")
    batch_name = col2.text_input("Batch Name (e.g., Dec_2025)", value="Dec_2025_Test")

    st.markdown("---")

    # Simplified UI: Mode selection and JSON loading are removed.
    st.subheader("Question Source: AI Generation")

    # AI Question Refresh checkbox - now mandatory and simplified
    auto_questions = st.checkbox(
        "Generate fresh AI questions for all levels",
        value=True,
        help="The AI will generate questions for all five levels before form creation."
    )

    if st.button("🚀 Create New Interview Batch", type="primary"):
        # run_form_generation now only takes batch_name, candidate_name, and main_folder_id
        run_form_generation(batch_name, candidate_name, DEFAULT_FOLDER_ID)

st.divider()

# --- 2. Run Evaluation (Placeholder) ---
st.header("2. Run Evaluation & Generate Feedback")
st.warning("Phase 5/6 (Evaluation and Reporting) modules are not yet implemented in the provided code.")

if st.button("📈 Run Evaluation & Generate Reports", disabled=True):
    st.info("Evaluation process starting...")