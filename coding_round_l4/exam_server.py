from flask import Flask, render_template, request, jsonify
import yaml, subprocess, os, random, sys, json
from datetime import datetime
import time

# =====================================================
# L4 EXAM EXPIRY CONFIG
# =====================================================
EXAM_DURATION_SECONDS = 6 * 60 * 60  # 6 hours
SERVER_START_TIME = time.time()

# =====================================================
# SERVER CONTEXT (PORT + UID)
# =====================================================
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
UID = sys.argv[2] if len(sys.argv) > 2 else "unknown"

BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)

app = Flask(__name__)

# =====================================================
# PER-CANDIDATE RESULT FILE (CRITICAL FIX)
# =====================================================
UID = os.environ.get("CANDIDATE_UID")

if not UID:
    raise RuntimeError("CANDIDATE_UID not set for L4 server")

RESULT_FILE = os.path.join(BASE, f"l4_result_{UID}.json")



with open("questions.yaml", "r", encoding="utf-8") as f:
    QUESTIONS = yaml.safe_load(f)

ASSIGNED_QUESTION = random.choice(QUESTIONS)

def is_exam_expired():
    return (time.time() - SERVER_START_TIME) > EXAM_DURATION_SECONDS

# ---------------- PARAM INFERENCE ----------------
def infer_params(sample_input):
    names = []
    for i, v in enumerate(sample_input):
        if isinstance(v, list):
            names.append(f"arr{i}")
        elif isinstance(v, str):
            names.append(f"s{i}")
        else:
            names.append(f"x{i}")
    return names

# ---------------- STARTER CODE ----------------
def generate_starter_code(question, lang):
    sample_input = question["public_tests"][0]["input"]
    params = infer_params(sample_input)
    args = ", ".join(params)

    if lang == "python":
        return f"""def solve({args}):
    pass
"""
    if lang == "javascript":
        return f"""function solve({args}) {{
}}
"""
    if lang == "java":
        java_args = []
        for p in params:
            if p.startswith("arr"):
                java_args.append(f"int[] {p}")
            else:
                java_args.append(f"String {p}")
        return f"""class Solution {{
    public static Object solve({", ".join(java_args)}) {{
        return null;
    }}
}}
"""

# ---------------- EXECUTORS ----------------
def run_python(code, args):
    p = subprocess.Popen(
        ["python3", "executors/run_python.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    out, _ = p.communicate(json.dumps({"code": code, "args": args}))
    return json.loads(out)

def run_js(code, args):
    p = subprocess.Popen(
        ["node", "executors/run_js.js"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    out, _ = p.communicate(json.dumps({"code": code, "args": args}))
    return json.loads(out)

def run_java(code, args):
    p = subprocess.Popen(
        ["bash", "executors/run_java.sh"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    out, _ = p.communicate(json.dumps({"code": code, "args": args}))
    return json.loads(out)

LANG_EXEC = {
    "python": run_python,
    "javascript": run_js,
    "java": run_java
}

# ---------------- ROUTES ----------------
@app.route("/")
def index():
    if is_exam_expired():
        return (
            "<h3>⏰ This coding test has expired.</h3>"
            "<p>Please contact HR for further instructions.</p>",
            403
        )

    return render_template(
        "index.html",
        question=ASSIGNED_QUESTION,
        starters={
            "python": generate_starter_code(ASSIGNED_QUESTION, "python"),
            "javascript": generate_starter_code(ASSIGNED_QUESTION, "javascript"),
            "java": generate_starter_code(ASSIGNED_QUESTION, "java"),
        }
    )


@app.route("/run_code", methods=["POST"])
def run_code():
    if is_exam_expired():
        return jsonify({
            "error": True,
            "message": "⏰ This coding test has expired. Submission is disabled."
        }), 403

    data = request.get_json(force=True)

    code = data["code"]
    lang = data["language"]
    submit = bool(data.get("submit", False))
    run_hidden = bool(data.get("run_hidden", False))

    # 🔹 PHASE 2: focus_lost is now WARNINGS count
    focus_lost = int(data.get("focus_lost", 0))

    public_tests = ASSIGNED_QUESTION["public_tests"]
    hidden_tests = ASSIGNED_QUESTION["hidden_tests"]

    tests = public_tests
    if run_hidden or submit:
        tests = public_tests + hidden_tests

    executor = LANG_EXEC[lang]
    passed = 0

    # 🔹 PHASE 1: structured per-test results
    test_results = []

    for idx, t in enumerate(tests):
        res = executor(code, t["input"])

        if res.get("returncode", 0) != 0:
            return jsonify({
                "error": True,
                "message": res.get("stderr", "Execution error")
            })

        actual = str(res.get("stdout", "")).strip()
        expected = str(t["expected"])
        is_passed = actual == expected

        if is_passed:
            passed += 1

        test_results.append({
            "index": idx + 1,
            "input": t["input"],
            "expected_output": expected,
            "actual_output": actual,
            "passed": is_passed,
            "visibility": "public" if t in public_tests else "hidden"
        })

    total = len(tests)
    score = round((passed / total) * 100, 2) if total else 0.0

    # 🔹 PASS / FAIL decided ONLY by score (65%)
    status = "PASS" if score >= 65 else "FAIL"

    # 🔹 Persist full L4 result
    if submit:
        with open(RESULT_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "passed": passed,
                "total": total,
                "score_percent": score,
                "language": lang,

                # warnings only (informational)
                "focus_lost": focus_lost,

                "status": status,
                "timestamp": datetime.utcnow().isoformat(),

                # 🔥 Core data
                "submitted_code": code,
                "test_cases": test_results
            }, f, indent=2)

    return jsonify({
        "passed": passed,
        "total": total,
        "score_percent": score,
        "status": status,
        "test_results": test_results,
        "focus_warnings": focus_lost
    })


if __name__ == "__main__":
    vm_ip = os.environ.get("VM_IP", "localhost")
    print(f"🚀 L4 server running at http://{vm_ip}:{PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=False)