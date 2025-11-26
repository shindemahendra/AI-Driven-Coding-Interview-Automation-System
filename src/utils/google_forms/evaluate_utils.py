def extract_mcq_answers(response_data):
    """Extract MCQ responses as {question_text: answer_value}"""

    answers = {}

    if "responses" not in response_data:
        return answers

    for submission in response_data["responses"]:
        if "answers" not in submission:
            continue

        for ans in submission["answers"].values():
            if "textAnswers" in ans:
                # Text answer (typed)
                text_vals = ans["textAnswers"].get("answers", [])
                if text_vals:
                    answers[ans.get("questionId", "Unknown ID")] = text_vals[0].get("value", "")
            elif "choiceAnswers" in ans:
                # MCQ selected answer
                choice_vals = ans["choiceAnswers"].get("values", [])
                if choice_vals:
                    answers[ans.get("questionId", "Unknown ID")] = choice_vals[0]

    return answers
