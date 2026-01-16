import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from src.utils.reports.ai_hr_summary import generate_ai_hr_summary


from src.utils.google_forms.form_api import get_drive_service


def generate_candidate_pdf_and_upload(
    uid: str,
    cand: dict,
    results: dict,
    drive_root_folder_id: str,
    local_tmp_dir: str,
):
    """
    Generates a detailed PDF report per candidate and uploads to Drive
    """

    os.makedirs(local_tmp_dir, exist_ok=True)

    safe_name = "_".join(cand["name"].split())
    filename = f"{safe_name}_{uid}.pdf"
    pdf_path = os.path.join(local_tmp_dir, filename)

    styles = getSampleStyleSheet()
    story = []

    # -------------------------------------------------
    # HEADER
    # -------------------------------------------------
    story.append(Paragraph("<b>Candidate Assessment Report</b>", styles["Title"]))
    story.append(Spacer(1, 0.3 * inch))

    story.append(Paragraph(f"<b>Name:</b> {cand['name']}", styles["Normal"]))
    story.append(Paragraph(f"<b>Email:</b> {cand['email']}", styles["Normal"]))
    story.append(Paragraph(f"<b>Role:</b> {cand['role']}", styles["Normal"]))
    story.append(Paragraph(
        f"<b>Date:</b> {datetime.now().strftime('%d %b %Y %H:%M')}",
        styles["Normal"]
    ))

    story.append(Spacer(1, 0.3 * inch))

    # -------------------------------------------------
    # ROUND-WISE SUMMARY
    # -------------------------------------------------
    story.append(Paragraph("<b>Round-wise Performance</b>", styles["Heading2"]))
    story.append(Spacer(1, 0.2 * inch))

    for rnd, res in results.items():
        score = res.get("score_percent", 0)
        status = res.get("status", "NA")

        story.append(
            Paragraph(
                f"<b>{rnd}</b> — Score: {score}% | Status: {status}",
                styles["Normal"]
            )
        )

    story.append(PageBreak())

    # -------------------------------------------------
    # L4 CODING DETAILS
    # -------------------------------------------------
    l4 = results.get("L4")
    if l4:
        story.append(Paragraph("<b>Coding Round (L4) Details</b>", styles["Heading2"]))
        story.append(Spacer(1, 0.2 * inch))

        code = l4.get("submitted_code", "Code not available")
        analysis = l4.get("analysis", "Analysis not available")

        story.append(Paragraph("<b>Submitted Code:</b>", styles["Normal"]))
        story.append(Spacer(1, 0.1 * inch))
        story.append(Paragraph(f"<pre>{code}</pre>", styles["Code"]))

        story.append(Spacer(1, 0.3 * inch))
        story.append(Paragraph("<b>Evaluation Summary:</b>", styles["Normal"]))
        story.append(Paragraph(analysis, styles["Normal"]))

    # -------------------------------------------------

    # -------------------------------------------------
    # AI-GENERATED HR SUMMARY
    # -------------------------------------------------
    story.append(PageBreak())
    story.append(Paragraph("<b>AI-Generated HR Summary</b>", styles["Heading2"]))
    story.append(Spacer(1, 0.2 * inch))

    ai_summary = generate_ai_hr_summary(cand, results)

    for line in ai_summary.split("\n"):
        story.append(Paragraph(line, styles["Normal"]))
        story.append(Spacer(1, 0.1 * inch))


    # CREATE PDF
    # -------------------------------------------------
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    doc.build(story)

    # -------------------------------------------------
    # UPLOAD TO GOOGLE DRIVE
    # -------------------------------------------------
    drive = get_drive_service()

    uploaded = drive.files().create(
        body={
            "name": filename,
            "parents": [drive_root_folder_id],
        },
        media_body=pdf_path,
        fields="id",
    ).execute()

    return uploaded["id"]
