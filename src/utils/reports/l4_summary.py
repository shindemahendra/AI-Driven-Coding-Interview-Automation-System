def summarize_round(round_name: str, result: dict) -> str:
    score = result.get("score_percent", 0)
    status = result.get("status", "NO_RESPONSE")

    if status == "NO_RESPONSE":
        return f"{round_name}: Not attempted."

    if score >= 85:
        return f"{round_name}: Strong performance with high accuracy."
    elif score >= 60:
        return f"{round_name}: Moderate performance with acceptable understanding."
    elif score > 0:
        return f"{round_name}: Basic attempt; improvement needed."
    else:
        return f"{round_name}: Unable to demonstrate required skills."


def generate_l4_summary(l4_result: dict) -> str:
    """
    Dedicated L4 coding summary
    """
    score = l4_result.get("score_percent", 0)

    if score >= 85:
        return (
            "Excellent coding skills demonstrated. "
            "Solution is logically sound and passes most or all test cases."
        )
    elif score >= 60:
        return (
            "Good problem-solving approach, but solution "
            "has partial correctness or misses edge cases."
        )
    else:
        return (
            "Candidate attempted the problem but could not "
            "produce a correct or complete solution."
        )
