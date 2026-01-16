import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from textwrap import wrap

from src.utils.reports.l4_summary import generate_l4_summary


def generate_l4_pdf(
    output_dir: str,
    uid: str,
    cand: dict,
    l4_result: dict,
) -> str:
    """
    Generates L4 Coding Round PDF and returns local file path
    """

    safe_name = "_".join(cand["name"].split())
    pdf_name = f"{safe_name}_{uid}.pdf"
    pdf_path = os.path.join(output_dir, pdf_name)

    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    y = height - 40

    def write(text):
        nonlocal y
        for line in wrap(text, 95):
            c.drawString(40, y, line)
            y -= 14
            if y < 40:
                c.showPage()
                y = height - 40

    # -------- Header --------
    write(f"Candidate Name : {cand['name']}")
    write(f"Email          : {cand['email']}")
    write(f"UID            : {uid}")
    write(f"Role           : {cand['role']}")
    write("")

    # -------- L4 Result --------
    write("L4 Coding Round Evaluation")
    write("-" * 90)

    write(f"Score %        : {l4_result.get('score_percent', 0)}")
    write(f"Status         : {l4_result.get('status', 'NO_RESPONSE')}")
    write(
        f"Test Cases     : "
        f"{l4_result.get('passed_test_cases', 0)} / "
        f"{l4_result.get('total_test_cases', 0)}"
    )

    write("")
    write("Evaluator Summary:")
    write(generate_l4_summary(l4_result))

    # -------- Submitted Code --------
    submitted_code = l4_result.get("submitted_code")
    if submitted_code:
        write("")
        write("Submitted Code:")
        write("-" * 90)
        write(submitted_code)

    c.save()
    return pdf_path
