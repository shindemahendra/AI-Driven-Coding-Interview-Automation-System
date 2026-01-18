# src/utils/google_forms/evaluate_round.py

import json
import os
from typing import Dict, Tuple, List, Any

from src.utils.google_forms.form_api import get_forms_service
from src.utils.google_forms.save_results_to_sheet import save_round_result

# =========================================================
# Helpers
# =========================================================

def clean(text):
    if text is None:
        return ""
    return " ".join(str(text).split()).strip()


# =========================================================
# GOOGLE FORM HELPERS (L1 / L2 / L3 / L5)
# =========================================================

def fetch_latest_answers(form_id: str) -> Dict[str, str]:
    forms = get_forms_service()
    resp = forms.forms().responses().list(formId=form_id).execute()
    responses = resp.get("responses", [])

    if not responses:
        return {}

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
    index: Dict[str, Tuple[str, str]] = {}

    for level, questions in candidate_data.items():
        if level in ("candidate", "L4"):
            continue
        if not isinstance(questions, list):
            continue

        for q in questions:
            title = clean(q.get("question"))
            correct = q.get("correct_answer")
            if title and correct is not None:
                index[title] = (str(correct).strip(), level)

    return index


from typing import Dict, Any
import os
import json


# =========================================================
# L4 EVALUATION (SINGLE SOURCE OF TRUTH)
# =========================================================
def evaluate_l4_round(result_path: str, candidate_data: dict) -> Dict[str, Any]:

    # -----------------------------------------------------
    # Case 1: No result file
    # -----------------------------------------------------
    if not os.path.exists(result_path):
        spreadsheet_id = save_round_result(
            uid=candidate_data["uid"],
            candidate_name=candidate_data["name"],
            email=candidate_data["email"],
            round_name="L4",
            total_questions=0,
            correct_answers=0,
            score_percent=0.0,
            status="NO_RESPONSE",
        )

        return {
            "round_name": "L4",
            "total_questions": 0,
            "correct_count": 0,
            "score_percent": 0.0,
            "status": "NO_RESPONSE",
            "spreadsheet_id": spreadsheet_id,
            "details": [],
            # NEW (safe defaults)
            "submitted_code": None,
            "test_cases": [],
            "passed_test_cases": 0,
            "failed_test_cases": 0,
        }

    # -----------------------------------------------------
    # Case 2: Result exists
    # -----------------------------------------------------
    with open(result_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    passed = int(data.get("passed", 0))
    total = int(data.get("total", 0))
    score_percent = float(data.get("score_percent", 0))
    focus_lost = int(data.get("focus_lost", 0))

    # ✅ PASS threshold changed to 65%
    status = "PASS" if score_percent >= 65 else "FAIL"

    # -----------------------------------------------------
    # Structured test case extraction (NEW)
    # -----------------------------------------------------
    raw_test_cases = data.get("test_cases", [])
    structured_test_cases = []

    for idx, tc in enumerate(raw_test_cases, start=1):
        expected = tc.get("expected_output")
        actual = tc.get("actual_output")

        structured_test_cases.append({
            "test_case_id": idx,
            "input": tc.get("input"),
            "expected_output": expected,
            "actual_output": actual,
            "passed": expected == actual,
        })

    failed = max(total - passed, 0)

    # -----------------------------------------------------
    # Save to Google Sheets (unchanged behavior)
    # -----------------------------------------------------
    spreadsheet_id = save_round_result(
        uid=candidate_data["uid"],
        candidate_name=candidate_data["name"],
        email=candidate_data["email"],
        round_name="L4",
        total_questions=total,
        correct_answers=passed,
        score_percent=score_percent,
        status=status,
        focus_violations=focus_lost,
    )

    # -----------------------------------------------------
    # Final result (BACKWARD + FORWARD compatible)
    # -----------------------------------------------------
    return {
        "round_name": "L4",
        "total_questions": total,
        "correct_count": passed,
        "score_percent": score_percent,
        "status": status,
        "spreadsheet_id": spreadsheet_id,

        # Existing UI-compatible field
        "details": [
    {
        "title": "Coding Test",
        "user_answer": f"{passed}/{total}",
        "correct_answer": ">= 65%",
        "is_correct": status == "PASS",
    },
    {
        "title": "Focus Warnings",
        "user_answer": str(focus_lost),
        "correct_answer": "Informational only",
        "is_correct": True,
    }
],

        # NEW structured fields (used by PDF)
        "submitted_code": data.get("submitted_code"),
        "test_cases": structured_test_cases,
        "passed_test_cases": passed,
        "failed_test_cases": failed,
    }
# =========================================================
# CORE EVALUATION (MCQ ROUNDS)
# =========================================================

def evaluate_round_core(form_id: str, json_path: str) -> Dict[str, Any]:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    candidate = data.get("candidate", {})
    uid = candidate.get("uid", "UNKNOWN_UID")
    candidate_name = candidate.get("name", "")
    email = candidate.get("email", "")

    # L4 shortcut
    if form_id == "L4":
        return evaluate_l4_round(
            f"question_bank/l4_results/{uid}.json",
            candidate,
        )

    question_index = build_question_index(data)
    user_answers_by_qid = fetch_latest_answers(form_id)

    forms = get_forms_service()
    form_def = forms.forms().get(formId=form_id).execute()
    items = form_def.get("items", [])

    total_questions = 0
    correct_count = 0
    details: List[Dict[str, Any]] = []

    for item in items:
        q_item = item.get("questionItem")
        if not q_item:
            continue

        title = clean(item.get("title", ""))
        qid = q_item.get("question", {}).get("questionId")
        user_answer = clean(user_answers_by_qid.get(qid, ""))

        total_questions += 1

        correct_answer, _ = question_index.get(title, (None, "UNKNOWN"))
        is_correct = correct_answer is not None and user_answer == clean(correct_answer)

        if is_correct:
            correct_count += 1

        details.append({
            "title": title,
            "user_answer": user_answer or "-",
            "correct_answer": correct_answer,
            "is_correct": is_correct,
        })

    if not user_answers_by_qid:
        score_percent = 0.0
        status = "NO_RESPONSE"
    else:
        score_percent = round((correct_count / total_questions) * 100, 2)
        status = "PASS" if score_percent >= 75 else "FAIL"

    # 🔑 CRITICAL FIX — round is determined by caller (L1/L2/L3/L5)
    round_name = next(
        (lvl for lvl in ["L1", "L2", "L3", "L5"] if lvl in json_path),
        "UNKNOWN",
    )

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
