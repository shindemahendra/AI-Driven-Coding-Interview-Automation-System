from flask import Flask, render_template, request, jsonify
import yaml, subprocess, os, random, sys, json
from datetime import datetime

# -------------------------------------------------
# PORT
# -------------------------------------------------
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5000

# -------------------------------------------------
# BASE
# -------------------------------------------------
BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)

app = Flask(__name__)

RESULT_FILE = os.path.join(BASE, "l4_result.json")

# -------------------------------------------------
# LOAD QUESTIONS
# -------------------------------------------------
with open("questions.yaml", "r", encoding="utf-8") as f:
    QUESTIONS = yaml.safe_load(f)

if not QUESTIONS:
    raise RuntimeError("questions.yaml empty")

ASSIGNED_QUESTION = random.choice(QUESTIONS)

# -------------------------------------------------
# PARAM INFERENCE (CRITICAL)
# -------------------------------------------------
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

# -------------------------------------------------
# STARTER CODE (NO *ARGS)
# -------------------------------------------------
def generate_starter_code(question, lang):
    sample_input = question["public_tests"][0]["input"]
    params = infer_params(sample_input)
    args = ", ".join(params)

    if lang == "python":
        return f"""def solve({args}):
    # Write your solution here
    pass
"""

    if lang == "javascript":
        return f"""function solve({args}) {{
    // Write your solution here
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
        // Write your solution here
        return null;
    }}
}}
"""

# -------------------------------------------------
# EXECUTORS (UNCHANGED)
# -------------------------------------------------
def run_python(code, args):
    p = subprocess.Popen(
        ["python3", "executors/run_python.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    out, err = p.communicate(json.dumps({"code": code, "args": args}))
    return json.loads(out)

def run_js(code, args):
    p = subprocess.Popen(
        ["node", "executors/run_js.js"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    out, err = p.communicate(json.dumps({"code": code, "args": args}))
    return json.loads(out)

def run_java(code, args):
    p = subprocess.Popen(
        ["bash", "executors/run_java.sh"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    out, err = p.communicate(json.dumps({"code": code, "args": args}))
    return json.loads(out)

LANG_EXEC = {
    "python": run_python,
    "javascript": run_js,
    "java": run_java
}

# -------------------------------------------------
# ROUTES
# -------------------------------------------------
@app.route("/")
def index():
    starters = {
        "python": generate_starter_code(ASSIGNED_QUESTION, "python"),
        "javascript": generate_starter_code(ASSIGNED_QUESTION, "javascript"),
        "java": generate_starter_code(ASSIGNED_QUESTION, "java"),
    }

    return render_template(
        "index.html",
        question=ASSIGNED_QUESTION,
        starters=starters
    )

@app.route("/run_code", methods=["POST"])
def run_code():
    data = request.get_json(force=True)

    code = data["code"]
    lang = data["language"]
    is_submit = bool(data.get("submit", False))
    focus_lost = int(data.get("focus_lost", 0))

    tests = ASSIGNED_QUESTION["public_tests"]
    if is_submit:
        tests += ASSIGNED_QUESTION["hidden_tests"]

    executor = LANG_EXEC[lang]
    passed = 0

    for t in tests:
        res = executor(code, t["input"])
        if str(res.get("stdout", "")).strip() == str(t["expected"]):
            passed += 1

    total = len(tests)
    score = round((passed / total) * 100, 2)

    if is_submit:
        with open(RESULT_FILE, "w") as f:
            json.dump({
                "score_percent": score,
                "passed": passed,
                "total": total,
                "language": lang,
                "focus_lost": focus_lost,
                "timestamp": datetime.utcnow().isoformat()
            }, f, indent=2)

    return jsonify({
        "passed": passed,
        "total": total,
        "finished": is_submit
    })

# -------------------------------------------------
# MAIN
# -------------------------------------------------
if __name__ == "__main__":
    print(f"🚀 L4 server running at http://localhost:{PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=False)
