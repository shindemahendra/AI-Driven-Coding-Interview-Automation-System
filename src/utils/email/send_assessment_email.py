def send_assessment_email(
    candidate_name: str,
    candidate_email: str,
    company_name: str,
    round_links: dict,   # MUST be FULL URLs (already built in UI)
    round_labels: dict,  # {"L1": "Aptitude", ...}
):
    import os
    import smtplib
    from email.message import EmailMessage

    SMTP_EMAIL = os.environ.get("SMTP_EMAIL")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
    SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))

    if not SMTP_EMAIL or not SMTP_PASSWORD:
        raise RuntimeError("SMTP credentials not configured")

    msg = EmailMessage()
    msg["Subject"] = f"Assessment Links – {company_name} Hiring Drive"
    msg["From"] = SMTP_EMAIL
    msg["To"] = candidate_email

    # -------------------------------------------------
    # HTML BODY (USES LINKS EXACTLY AS UI PROVIDES)
    # -------------------------------------------------
    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        <p>Dear <b>{candidate_name}</b>,</p>

        <p>
          Welcome to <b>{company_name}</b>!<br>
          Please find below your assessment links for today.
        </p>

        <h3>Assessment Links</h3>
        <ul>
    """

    for rnd in ["L1", "L2", "L3", "L4", "L5", "L6"]:
        url = round_links.get(rnd)
        if not url:
            continue

        label = round_labels.get(rnd, rnd)

        # ✅ USE URL AS-IS (NO MODIFICATION)
        html += f"""
          <li>
            <a href="{url}" target="_blank"
               style="color:#1a73e8; text-decoration:none; font-weight:600;">
              {label}
            </a>
          </li>
        """

    html += """
        </ul>

        <h4>Important Instructions</h4>
        <ul>
          <li>Except <b>Coding Round</b>, all rounds are MCQs</li>
          <li>Submit button activates only after answering all questions</li>
          <li>Please maintain silence during the assessment</li>
          <li>Contact the coordinator if you face any issues</li>
        </ul>

        <p>
          Best of luck!<br><br>
          Regards,<br>
          <b>Aziro Technologies Pvt Ltd</b><br>
          Hiring Team<br>
          aziro-ai-hiring@aziro.com
        </p>
      </body>
    </html>
    """

    msg.set_content("Please open this email in HTML format.")
    msg.add_alternative(html, subtype="html")

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)
