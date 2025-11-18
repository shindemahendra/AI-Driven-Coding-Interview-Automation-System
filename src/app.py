import streamlit as st
import pandas as pd
# Import the actual functional modules
from form_generator import create_interview_form, populate_form_with_questions
from ai_generator import generate_questions_for_level

# --- Configuration ---
DEFAULT_FOLDER_ID = "YOUR_GOOGLE_DRIVE_FOLDER_ID"
LEVELS_CONFIG = {
    'L1': 'Logical Puzzles', 'L2': 'MCQs', 'L4': 'Coding', 'L5': 'Soft-skill Situational Questions'
}


def run_form_generation(batch_name, folder_id, auto_questions):
    """Executes the full Form Creation and Question Population workflow (P2/P3)."""
    st.info(f"Initiating new batch: **{batch_name}**...")
    master_tracker = []

    for level, q_type in LEVELS_CONFIG.items():
        st.markdown(f"**Creating {level} ({q_type})...**")
        try:
            # P2: Create Form & Link Sheet
            form_id, form_url, sheet_id, sheet_url = create_interview_form(level, batch_name, folder_id)

            # P3: Populate Questions
            questions_data = []
            if auto_questions:
                questions_data = generate_questions_for_level(level, q_type)

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
st.markdown("Central dashboard to manage interview batches and evaluation.")
st.divider()

# --- 1. Create New Interview Batch ---
with st.container():
    st.header("1. Create New Interview Batch")

    col1, col2, col3 = st.columns(3)
    batch_name = col1.text_input("Batch Name", value="Dec_2025")
    folder_id = col2.text_input("Google Drive Folder ID", value=DEFAULT_FOLDER_ID)
    auto_questions = col3.checkbox("AI Question Refresh", value=True)

    if st.button("🚀 Create New Interview Batch", type="primary"):
        if folder_id == "YOUR_GOOGLE_DRIVE_FOLDER_ID":
            st.error("Please provide a valid Google Drive Folder ID.")
        else:
            run_form_generation(batch_name, folder_id, auto_questions)

st.divider()

# --- 2. Run Evaluation (Placeholder) ---
st.header("2. Run Evaluation & Generate Feedback")
st.warning("Requires Phase 5 (Evaluator) and Phase 6 (Report Generator) to be implemented.")

if st.button("📈 Run Evaluation & Generate Reports", disabled=True):
    st.info("Evaluation process starting...")
    # Placeholder for running the process_interview_batch function (P5/P6)

# End of app.py