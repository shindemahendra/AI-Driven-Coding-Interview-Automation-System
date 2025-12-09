from flask import Flask, render_template, request, jsonify
import yaml
import subprocess
import tempfile
import os
import random
import sys

app = Flask(__name__)

# --- Load questions from YAML ---
with open("questions.yaml", "r", encoding="utf-8") as f:
    QUESTIONS = yaml.safe_load(f)

if not QUESTIONS or not isinstance(QUESTIONS, list):
    raise RuntimeError("questions.yaml is invalid or empty")

# Pick one random question for this server run
ASSIGNED_QUESTION = random.choice(QUESTIONS)


@app.route("/")
def index():
    return render_template("index.html", question=ASSIGNED_QUESTION)


@app.route("/run_code", methods=["POST"])
def run_code():
    data = request.get_json(force=True) or {}
    code = data.get("code", "")
    is_submit = bool(data.get("submit", False))

    question = ASSIGNED_QUESTION
    public_tests = question.get("public_tests", [])
    hidden_tests = question.get("hidden_tests", [])

    # For Run: only public tests. For Submit: public + hidden
    tests = public_tests + hidden_tests if is_submit else public_tests

    if not tests:
        return jsonify({
            "output": "No tests configured for this question.",
            "finished": is_submit,
            "passed": 0,
            "total": 0
        })

    results_lines = []
    passed = 0
    total = len(tests)

    for idx, test in enumerate(tests, start=1):
        test_input = test["input"]
        expected = test["expected"]
        temp_name = None

        try:
            # Create a temp .py file with user's code + harness
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as tmp:
                temp_name = tmp.name
                tmp.write(code)
                tmp.write("\n\n# === Auto-generated harness ===\n")
                tmp.write("def _run_test():\n")
                tmp.write(f"    args = {repr(test_input)}\n")
                tmp.write("    if isinstance(args, (list, tuple)):\n")
                tmp.write("        result = solve(*args)\n")
                tmp.write("    else:\n")
                tmp.write("        result = solve(args)\n")
                tmp.write("    print(result)\n\n")
                tmp.write("if __name__ == '__main__':\n")
                tmp.write("    _run_test()\n")

            proc = subprocess.run(
                [sys.executable, temp_name],
                capture_output=True,
                text=True,
                timeout=5
            )

            if proc.returncode != 0:
                # Runtime error / Syntax error
                out = (proc.stderr or "").strip() or "Runtime error"
                ok = False
            else:
                stdout = proc.stdout.strip()
                last_line = stdout.splitlines()[-1] if stdout else ""
                out = last_line
                ok = (str(out) == str(expected))

            if ok:
                passed += 1

            results_lines.append(
                f"Test {idx} → {'PASS' if ok else 'FAIL'}\n"
                f"Input: {test_input}\n"
                f"Expected: {expected}\n"
                f"Output: {out}\n"
            )

        except Exception as e:
            results_lines.append(
                f"Test {idx} → ERROR\n"
                f"Input: {test_input}\n"
                f"Error: {e}\n"
            )
        finally:
            if temp_name and os.path.exists(temp_name):
                os.remove(temp_name)

    header = "FINAL SUBMISSION RESULTS" if is_submit else "PUBLIC TEST RUN"
    output_msg = f"========== {header} ==========\n"
    output_msg += f"Passed: {passed}/{total}\n\n"
    output_msg += "\n".join(results_lines)

    return jsonify({
        "output": output_msg,
        "finished": is_submit,
        "passed": passed,
        "total": total
    })


if __name__ == "__main__":
    print("Assigned question:", ASSIGNED_QUESTION["title"])
    print("Server running at: http://localhost:5000")
    app.run(debug=True)
