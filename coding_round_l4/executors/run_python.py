import sys, json

def main():
    try:
        payload = json.loads(sys.stdin.read())
        code = payload["code"]
        args = payload["args"]

        temp_file = "temp_user_code.py"
        with open(temp_file, "w") as f:
            f.write(code)
            f.write("\n\n")
            f.write("def _runner():\n")
            f.write(f"    a = {repr(args)}\n")
            f.write("    import builtins\n")
            f.write("    from __main__ import solve\n")
            f.write("    # handle args type\n")
            f.write("    if isinstance(a, list):\n")
            f.write("        res = solve(*a)\n")
            f.write("    else:\n")
            f.write("        res = solve(a)\n")
            f.write("    print(res)\n")
            f.write("\nif __name__ == '__main__': _runner()")

        # execute user code
        import subprocess
        result = subprocess.run(
            [sys.executable, temp_file],
            capture_output=True,
            text=True,
            timeout=5
        )

        print(json.dumps({
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode
        }))

    except Exception as e:
        print(json.dumps({
            "stdout": "",
            "stderr": str(e),
            "returncode": -1
        }))

if __name__ == "__main__":
    main()
