from flask import Flask, render_template, request, jsonify
import yaml
import subprocess
import tempfile
import os
import random
import sys

# -------------------------------------------------
# FIX 1️⃣ : FORCE CORRECT WORKING DIRECTORY
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

app = Flask(__name__)

# -------------------------------------------------
# FIX 2️⃣ : PORT HANDLING
# -------------------------------------------------
PORT = 5000
if len(sys.argv) > 1:
    try:
        PORT = int(sys.argv[1])
    except:
        pass

# -------------------------------------------------
# Load questions.yaml (NOW SAFE)
# -------------------------------------------------
with open("questions.yaml", "r", encoding="utf-8") as f:
    QUESTIONS = yaml.safe_load(f)

if not QUESTIONS:
    raise RuntimeError("questions.yaml is empty or invalid")

ASSIGNED_QUESTION = random.choice(QUESTIONS)


@app.route("/")
def index():
    return render_template("index.html", question=ASSIGNED_QUESTION)


@app.route("/run_code", methods=["POST"])
def run_code():
    data = request.get_json(force=True) or {}
    code = data.get("code", "")
    is_submit = bool(data.get("submit", False))
    focus_violations = int(data.get("focus_violations", 0))

    public_tests = ASSIGNED_QUESTION.get("public_tests", [])
    hidden_tests = ASSIGNED_QUESTION.get("hidden_tests", [])
    tests = public_tests + hidden_tests if is_submit else public_tests

    passed = 0
    total = len(tests)
    results = []

    for i, t in enumerate(tests, 1):
        temp = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                temp = f.name
                f.write(code)
                f.write("\n\ndef _run():\n")
                f.write(f"    args = {repr(t['input'])}\n")
                f.write("    r = solve(*args) if isinstance(args, (list, tuple)) else solve(args)\n")
                f.write("    print(r)\n\n")
                f.write("if __name__ == '__main__': _run()\n")

            proc = subprocess.run(
                [sys.executable, temp],
                capture_output=True,
                text=True,
                timeout=5
            )

            output = proc.stdout.strip().splitlines()[-1] if proc.returncode == 0 else proc.stderr
            ok = str(output) == str(t["expected"])
            if ok:
                passed += 1

            results.append(f"Test {i}: {'PASS' if ok else 'FAIL'}")

        finally:
            if temp and os.path.exists(temp):
                os.remove(temp)

    score = round((passed / total) * 100, 2) if total else 0
    status = "PASS" if score >= 75 and focus_violations == 0 else "FAIL"

    return jsonify({
        "finished": is_submit,
        "passed": passed,
        "total": total,
        "score_percent": score,
        "focus_violations": focus_violations,
        "status": status,
        "output": "\n".join(results)
    })


if __name__ == "__main__":
    print(f"🚀 L4 server running on http://localhost:{PORT}")
    app.run(host="127.0.0.1", port=PORT, debug=False)
