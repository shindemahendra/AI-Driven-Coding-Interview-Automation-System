# src/utils/google_forms/evaluate_round.py

import json
from typing import Dict, Tuple, List, Any

from src.utils.google_forms.form_api import get_forms_service
from src.utils.google_forms.save_results_to_sheet import save_round_result


def clean(text):
    if text is None:
        return ""
    # Flatten newlines + extra spaces
    return " ".join(str(text).split()).strip()


def fetch_latest_answers(form_id: str) -> Dict[str, str]:
    """
    Returns: {questionId: user_answer_text} for the latest submission.
    """
    forms = get_forms_service()

    resp = forms.forms().responses().list(formId=form_id).execute()
    responses = resp.get("responses", [])
    if not responses:
        print("❌ No responses found for this form.")
        return {}

    # Sort by lastSubmittedTime / createTime to get MOST RECENT
    responses.sort(
        key=lambda r: r.get("lastSubmittedTime", r.get("createTime", "")),
    )
    latest = responses[-1]

    answers_map = {}
    for qid, ans in latest.get("answers", {}).items():
        text_answers = ans.get("textAnswers", {}).get("answers", [])
        if text_answers:
            answers_map[qid] = clean(text_answers[0].get("value", ""))

    return answers_map


def build_question_index(candidate_data: dict) -> Dict[str, Tuple[str, str]]:
    """
    Build map: question_title_clean -> (correct_answer, level)
    Levels: L1, L2, L3, L5 (skip candidate + L4).
    """
    index: Dict[str, Tuple[str, str]] = {}
    for level, questions in candidate_data.items():
        if level in ("candidate", "L4"):
            continue
        if not isinstance(questions, list):
            continue

        for q in questions:
            title = clean(q.get("question"))
            correct = q.get("correct_answer")
            if not title or correct is None:
                continue
            index[title] = (str(correct).strip(), level)

    return index


def evaluate_round_core(form_id: str, json_path: str) -> Dict[str, Any]:
    """
    Core evaluation logic usable from both:
      - CLI (terminal)
      - Streamlit UI

    Returns a dict with:
      uid, candidate_name, email, round_name,
      total_questions, correct_count, score_percent,
      status, spreadsheet_id, details[]
    """
    # -------------------------
    # Load candidate JSON
    # -------------------------
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    candidate = data.get("candidate", {})
    uid = candidate.get("uid", "UNKNOWN_UID")
    candidate_name = candidate.get("name", "UNKNOWN_NAME")
    email = candidate.get("email", "")

    # Maps question title -> (correct_answer, level)
    question_index = build_question_index(data)

    # -------------------------
    # Fetch latest answers
    # -------------------------
    print("\n📩 Fetching form responses...")
    user_answers_by_qid = fetch_latest_answers(form_id)
    if not user_answers_by_qid:
        # No responses yet
        return {
            "uid": uid,
            "candidate_name": candidate_name,
            "email": email,
            "round_name": "UNKNOWN",
            "total_questions": 0,
            "correct_count": 0,
            "score_percent": 0.0,
            "status": "NO_RESPONSES",
            "spreadsheet_id": None,
            "details": [],
        }

    # -------------------------
    # Fetch form structure (to map questionId → question title)
    # -------------------------
    print("\n📌 Fetching form structure...")
    forms = get_forms_service()
    form_def = forms.forms().get(formId=form_id).execute()
    items = form_def.get("items", [])

    # -------------------------
    # Evaluate answers
    # -------------------------
    print("\n🧠 Evaluating answers...\n")

    total_questions = 0
    correct_count = 0
    level_counts: Dict[str, int] = {}
    details: List[Dict[str, Any]] = []

    for item in items:
        q_item = item.get("questionItem")
        if not q_item:
            continue

        title = clean(item.get("title", ""))
        question = q_item.get("question", {})
        qid = question.get("questionId")

        if not qid or not title:
            continue

        user_answer = clean(user_answers_by_qid.get(qid, ""))
        if not user_answer:
            # user skipped this question
            continue

        total_questions += 1

        correct_answer = None
        level = "UNKNOWN"

        if title in question_index:
            correct_answer, level = question_index[title]
            level_counts[level] = level_counts.get(level, 0) + 1

        is_correct = bool(
            correct_answer is not None and user_answer == clean(correct_answer)
        )

        print(f"Q: {title}")
        print(f"🟣 User Answer: {user_answer}")
        print(f"🟢 Correct: {correct_answer}\n")

        if is_correct:
            correct_count += 1

        details.append(
            {
                "title": title,
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "level": level,
            }
        )

    if total_questions == 0:
        print("❌ No evaluatable questions found (maybe no matching titles).")
        return {
            "uid": uid,
            "candidate_name": candidate_name,
            "email": email,
            "round_name": "UNKNOWN",
            "total_questions": 0,
            "correct_count": 0,
            "score_percent": 0.0,
            "status": "NO_EVALUATABLE_QUESTIONS",
            "spreadsheet_id": None,
            "details": [],
        }

    score_percent = round((correct_count / total_questions) * 100, 2)
    status = "PASS" if score_percent >= 75.0 else "FAIL"

    # Determine round name from majority of matched questions
    if level_counts:
        round_name = max(level_counts, key=level_counts.get)
    else:
        round_name = "UNKNOWN"

    print("=======================================")
    print(f"Total Questions: {total_questions}")
    print(f"Correct: {correct_count}")
    print(f"Score: {score_percent}% → {'PASSED ✅' if status == 'PASS' else 'FAILED ❌'}")
    print(f"Detected Round: {round_name}")
    print("=======================================\n")

    # -------------------------
    # Save to Google Sheet
    # -------------------------
    spreadsheet_id = save_round_result(
        uid=uid,
        candidate_name=candidate_name,
        email=email,
        round_name=round_name,
        total_questions=total_questions,
        correct_answers=correct_count,
        score_percent=score_percent,
        status=status,
    )

    print(f"📊 Result stored in spreadsheet: {spreadsheet_id}\n")

    return {
        "uid": uid,
        "candidate_name": candidate_name,
        "email": email,
        "round_name": round_name,
        "total_questions": total_questions,
        "correct_count": correct_count,
        "score_percent": score_percent,
        "status": status,
        "spreadsheet_id": spreadsheet_id,
        "details": details,
    }


def evaluate_round(form_id: str, json_path: str):
    """
    CLI-friendly wrapper (kept for terminal usage).
    """
    result = evaluate_round_core(form_id, json_path)
    if result["status"] in ("NO_RESPONSES", "NO_EVALUATABLE_QUESTIONS"):
        print(f"⚠ Status: {result['status']}")
    else:
        print("✅ Evaluation finished.")


if __name__ == "__main__":
    form_id = input("Enter Google Form ID: ").strip()
    json_path = input("Enter JSON path used for this round: ").strip()
    evaluate_round(form_id, json_path)
