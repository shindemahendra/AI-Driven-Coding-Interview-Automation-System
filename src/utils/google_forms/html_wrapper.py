def generate_timed_html(form_id, minutes, output_path, title="Timed Test"):
    """
    Generates an HTML file that embeds a Google Form inside a timed wrapper.
    When time expires, the form hides and a message appears.
    """

    form_url = f"https://docs.google.com/forms/d/{form_id}/viewform"

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 20px;
            text-align: center;
        }}
        #timer {{
            font-size: 28px;
            font-weight: bold;
            color: #d9534f;
            margin-bottom: 20px;
        }}
        #form-container {{
            width: 100%;
            max-width: 800px;
            margin: auto;
        }}
        iframe {{
            width: 100%;
            height: 900px;
            border: none;
        }}
        #time-up {{
            display: none;
            font-size: 26px;
            color: #d9534f;
            font-weight: bold;
            margin-top: 40px;
        }}
    </style>
</head>
<body>

<h2>{title}</h2>

<div id="timer">Time Remaining: <span id="countdown"></span></div>

<div id="form-container">
    <iframe src="{form_url}"></iframe>
</div>

<div id="time-up">⛔ Time is up! The form is no longer available.</div>

<script>
    let total_seconds = {minutes} * 60;

    function updateTimer() {{
        if (total_seconds <= 0) {{
            document.getElementById("form-container").style.display = "none";
            document.getElementById("time-up").style.display = "block";
            return;
        }}

        let mins = Math.floor(total_seconds / 60);
        let secs = total_seconds % 60;

        document.getElementById("countdown").innerHTML =
            mins.toString().padStart(2, '0') + ":" +
            secs.toString().padStart(2, '0');

        total_seconds--;
        setTimeout(updateTimer, 1000);
    }}

    updateTimer();
</script>

</body>
</html>
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✅ Timed HTML created: {output_path}")
