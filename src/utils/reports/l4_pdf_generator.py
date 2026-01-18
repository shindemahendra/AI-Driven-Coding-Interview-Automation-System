import os
from textwrap import wrap
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from src.utils.reports.l4_summary import generate_l4_summary


def generate_l4_pdf(
    output_dir: str,
    uid: str,
    cand: dict,
    all_results: dict,   # IMPORTANT: full results, not only L4
) -> str:
    """
    Generates a detailed PDF report:
    - Summary of ALL rounds (L1–L6)
    - Detailed L4 Coding Round section
    """

    safe_name = "_".join(cand["name"].split())
    pdf_name = f"{safe_name}_{uid}.pdf"
    pdf_path = os.path.join(output_dir, pdf_name)

    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    y = height - 40

    def write(text="", gap=14):
        nonlocal y
        for line in wrap(str(text), 95):
            c.drawString(40, y, line)
            y -= gap
            if y < 40:
                c.showPage()
                y = height - 40

    # ============================================================
    # HEADER
    # ============================================================
    write(f"Candidate Name : {cand['name']}")
    write(f"Email          : {cand['email']}")
    write(f"UID            : {uid}")
    write(f"Role           : {cand['role']}")
    write("")
    write("=" * 95)

    # ============================================================
    # ALL ROUNDS SUMMARY
    # ============================================================
    write("ROUND-WISE SUMMARY")
    write("-" * 95)

    from src.utils.reports.l4_summary import summarize_round

    for rnd in ["L1", "L2", "L3", "L4", "L5", "L6"]:
        res = all_results.get(rnd)
        if not res:
            continue

        write(summarize_round(rnd, res))

    write("")
    write("=" * 95)

    # ============================================================
    # L4 CODING ROUND (DETAILED)
    # ============================================================
    l4 = all_results.get("L4")
    if not l4:
        write("L4 Coding Round was not attempted.")
        c.save()
        return pdf_path

    write("L4 CODING ROUND – DETAILED EVALUATION")
    write("-" * 95)

    score = l4.get("score_percent", 0)
    status = l4.get("status", "NO_RESPONSE")

    test_cases = l4.get("test_cases", [])
    passed = sum(1 for t in test_cases if t.get("passed"))
    total = len(test_cases)
    failed = total - passed

    write(f"Score           : {score}%")
    write(f"Status          : {status}")
    write(f"Test Cases      : {passed} Passed / {failed} Failed / {total} Total")
    write("")

    # ============================================================
    # Evaluator Summary
    # ============================================================
    write("Evaluator Summary:")
    write(generate_l4_summary(l4))
    write("")
    write("-" * 95)

    # ============================================================
    # Test Case Details
    # ============================================================
    if test_cases:
        write("Test Case Details:")
        for idx, tc in enumerate(test_cases, start=1):
            write(f"Test Case {idx}:")
            write(f"Input    : {tc.get('input')}")
            write(f"Expected : {tc.get('expected')}")
            write(f"Actual   : {tc.get('actual')}")
            write(f"Result   : {'PASS' if tc.get('passed') else 'FAIL'}")
            write("-" * 60)
    else:
        write("No test case execution data available.")

    write("")
    write("=" * 95)

    # ============================================================
    # SUBMITTED CODE
    # ============================================================
    submitted_code = l4.get("submitted_code")
    if submitted_code:
        write("SUBMITTED CODE:")
        write("-" * 95)
        write(submitted_code)
    else:
        write("No code submission found.")

    c.save()
    return pdf_path
