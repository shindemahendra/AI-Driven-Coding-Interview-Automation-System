from flask import Flask, render_template, request, jsonify
import yaml, subprocess, os, random, sys, json
from datetime import datetime

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)

app = Flask(__name__)
RESULT_FILE = os.path.join(BASE, "l4_result.json")

with open("questions.yaml", "r", encoding="utf-8") as f:
    QUESTIONS = yaml.safe_load(f)

ASSIGNED_QUESTION = random.choice(QUESTIONS)

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
    data = request.get_json(force=True)

    code = data["code"]
    lang = data["language"]
    submit = bool(data.get("submit", False))
    run_hidden = bool(data.get("run_hidden", False))
    focus_lost = int(data.get("focus_lost", 0))

    public_tests = ASSIGNED_QUESTION["public_tests"]
    hidden_tests = ASSIGNED_QUESTION["hidden_tests"]

    tests = public_tests
    if run_hidden or submit:
        tests = public_tests + hidden_tests

    executor = LANG_EXEC[lang]
    passed = 0

    # ➕ NEW: collect per-test results (additive)
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

        # ➕ NEW: record test details
        test_results.append({
            "index": idx + 1,
            "input": t["input"],
            "expected": expected,
            "actual": actual,
            "passed": is_passed,
            "visibility": "public" if t in public_tests else "hidden"
        })

    total = len(tests)
    score = round((passed / total) * 100, 2)

    status = "PASS"
    if score < 75:
        status = "FAIL"

    if submit:
        with open(RESULT_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "passed": passed,
                "total": total,
                "score_percent": score,
                "language": lang,
                "focus_lost": focus_lost,
                "status": status,
                "timestamp": datetime.utcnow().isoformat()
            }, f, indent=2)

    return jsonify({
        "passed": passed,
        "total": total,
        "score_percent": score,
        "status": status,

        # ➕ NEW FIELD (safe, optional)
        "test_results": test_results
    })

if __name__ == "__main__":
    vm_ip = os.environ.get("VM_IP", "localhost")
    print(f"🚀 L4 server running at http://{vm_ip}:{PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=False)
