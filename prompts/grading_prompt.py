import json


def get_grading_prompt(answer_key: str, submission_text: str, rubric: dict, strictness_level: int) -> str:
    return f"""
    You are grading a student submission. Here are the key components:

    ANSWER KEY:
    {answer_key}

    STUDENT SUBMISSION:
    {submission_text}

    RUBRIC:
    {json.dumps(rubric, indent=2)}

    Please grade this submission with a strictness level of {strictness_level}/20 
    (where 1 is most lenient and 20 is most strict).

    Consider partial credit where appropriate. Look for key concepts and understanding 
    even if the exact wording differs from the answer key.

    Provide your evaluation in this JSON format:
    {{
        "student_name": "Name from submission if available",
        "score": <total_score>,
        "total": <maximum_possible_score>,
        "mistakes": {{
            "<section_name>": {{
                "deductions": <points_deducted>,
                "reasons": "Detailed explanation of deductions"
            }}
        }},
        "grading_feedback": "Comprehensive feedback for improvement"
    }}
    """ 