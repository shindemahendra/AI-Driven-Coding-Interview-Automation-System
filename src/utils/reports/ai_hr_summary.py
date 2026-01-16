def generate_ai_hr_summary(cand: dict, results: dict) -> str:
    """
    Generates a human-readable HR summary using evaluation results.
    Safe, fast, deterministic (no external API).
    """

    scores = []
    strengths = []
    concerns = []

    for rnd, res in results.items():
        score = res.get("score_percent", 0)
        status = res.get("status", "NA")

        scores.append(score)

        if score >= 80:
            strengths.append(f"{rnd} shows strong performance")
        elif score < 40:
            concerns.append(f"{rnd} needs improvement")

    avg_score = round(sum(scores) / len(scores), 2) if scores else 0

    if avg_score >= 80:
        recommendation = "Strong candidate. Recommended for next round."
    elif avg_score >= 60:
        recommendation = "Good candidate. Can be considered with further evaluation."
    else:
        recommendation = "Candidate does not meet current hiring expectations."

    summary = f"""
Overall Performance Summary:

• Average Score: {avg_score}%
• Strengths: {", ".join(strengths) if strengths else "No major strengths observed"}
• Concerns: {", ".join(concerns) if concerns else "No major concerns observed"}

HR Recommendation:
{recommendation}
    """

    return summary.strip()
