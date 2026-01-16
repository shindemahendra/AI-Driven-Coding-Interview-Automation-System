def generate_l4_summary(l4_result: dict) -> str:
    """
    Generates a short, HR-friendly summary for L4 coding round
    """

    score = l4_result.get("score_percent", 0)
    passed = l4_result.get("passed_test_cases", 0)
    total = l4_result.get("total_test_cases", 0)
    status = l4_result.get("status", "NO_RESPONSE")

    if status != "PASS" or score == 0:
        return "Candidate was unable to provide a working solution."

    if score >= 85 and passed == total:
        return (
            "Strong coding skills demonstrated. "
            "Solution passed all test cases with correct logic."
        )

    if score >= 60:
        return (
            "Moderate performance. "
            "Solution passed some test cases but requires optimization or edge case handling."
        )

    return (
        "Basic attempt observed. "
        "Solution logic is incomplete or fails multiple test cases."
    )
