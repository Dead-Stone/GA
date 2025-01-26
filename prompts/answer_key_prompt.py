import json


def get_answer_key_prompt(questions_text: str, rubric: dict) -> str:
    return f"""
    Given these questions:
    {questions_text}
    
    And this grading rubric:
    {json.dumps(rubric, indent=2)}
    
    Please generate a detailed answer key that:
    1. Provides correct answers for each question
    2. Explains the reasoning behind each answer
    3. Highlights key points that should be present in student responses
    4. Aligns with the rubric criteria
    
    Format the answer key in a clear, structured way.
    """ 