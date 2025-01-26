from datetime import datetime
import logging
import re
import google.generativeai as genai
from typing import Dict, Any
import json
from prompts.answer_key_prompt import get_answer_key_prompt
from prompts.grading_prompt import get_grading_prompt 
from prompts.image_prompt import get_image_description_prompt

class GradingService:
    def __init__(self, api_key: str):
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        genai.configure(api_key=api_key)

    def grade_submission(self, 
                         submission_text: str, 
                         answer_key: str, 
                         rubric: Dict[str, Any], 
                         strictness_level: int = 1) -> Dict[str, Any]:
        try:
            prompt = get_grading_prompt(answer_key, submission_text, rubric, strictness_level)
            response = self.model.generate_content(prompt)
            logging.info(f"Grading response: {response.text}")
            
            # Extract JSON content from the response
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON content found in the response")

            json_content = json_match.group(0)
            response_data = json.loads(json_content)
            return {
                'score': float(response_data.get('score', 0)),
                'total': float(response_data.get('total', 100)),
                'mistakes': response_data.get('mistakes', {}),
                'grading_feedback': response_data.get('grading_feedback', '')
            }
        except json.JSONDecodeError as e:
            logging.error(f"JSON decoding error: {e}")
            logging.error(f"Raw response: {response.text}")
            raise
        except Exception as e:
            logging.error(f"Grading error: {e}")
            raise

    def batch_grade(self, submissions: Dict[str, str], answer_key: str, rubric: Dict[str, Any]) -> Dict[str, Any]:
        results = {}
        for student_name, submission in submissions.items():
            try:
                if not submission.strip():  # Skip empty submissions
                    logging.warning(f"Submission for {student_name} is empty. Skipping.")
                    results[student_name] = self._create_error_result()
                    continue

                result = self.grade_submission(submission, answer_key, rubric)
                results[student_name] = result
            except Exception as e:
                logging.error(f"Error grading {student_name}: {e}")
                results[student_name] = self._create_error_result()
        logging.info(f"Grading completed for {len(results)} submissions.")
        return results

    def generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        total_submissions = len(results)
        total_score = sum(result['score'] for result in results.values())
        average_score = total_score / total_submissions if total_submissions > 0 else 0
        passing_count = sum(1 for result in results.values() if result['score'] >= 70)

        summary = {
            "batch_info": {
                "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "timestamp": datetime.now().isoformat(),
                "total_submissions": total_submissions
            },
            "summary_stats": {
                "average_score": average_score,
                "passing_count": passing_count,
                "submission_count": total_submissions
            },
            "student_results": results
        }
        return summary

    def _create_error_result(self) -> Dict[str, Any]:
        return {
            'score': 0,
            'total': 100,
            'mistakes': {},
            'grading_feedback': 'Error occurred during grading'
        }